"""Prior provenance, review gates and exact inference checks; providers are always fake."""
import asyncio
from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from labton.cli import main
from labton.config import ConfigurationError
from labton.prior_math import posterior_sensitivity
from labton.priors import (PriorError, apply_priors, approve, check_protocol, load_approved,
                           runtime_priors, suggest, verify_frozen_files, write_record)
from labton.study import plans, run_variant
import test_providers as fixtures


class PriorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        (self.root / "setup/priors").mkdir(parents=True)
        (self.root / "prior.md").write_text("External prior-only cohort: examine applicability and limitations.")
        self.write("validation.json", {"successes": 1, "trials": 10, "note": "VALIDATION_NOT_FOR_ELICITOR"})
        self.panels = {phase: {kind: [100 * i + 10 * j + k for k in range(3)]
                              for j, kind in enumerate(("calibration", "null", "fault"))}
                       for i, phase in enumerate(("development", "confirmation"))}
        self.write("likelihood.json", self.panels)
        self.write("domain.yaml", {"adapter_kind": "memory_policy.v1", "private_seed_file": "likelihood.json",
                                  "protocol": {"steps": 192, "alpha_targets": [.1]}})
        def evidence(name, file, dataset):
            return {"id": name, "file": file, "dataset_id": dataset, "observation_ids": [name + ":unit"],
                    "lineage_ids": [], "relevance": "Reviewed population and observation unit."}
        self.protocol = {"schema_version": 1,
            "target": {"id": "run_false_alarms", "parameter": "Run alarm probability at alpha .1",
                       "population": "Synthetic fixed-horizon pilot", "observation_unit": "independent_run",
                       "success_definition": "At least one false alarm"}, "likelihood": "binomial",
            "candidates": [{"id": "broad", "family": "beta", "a": 1, "b": 1, "rationale": "Reference"},
                           {"id": "cautious", "family": "beta", "a": 1, "b": 9, "rationale": "External data"},
                           {"id": "stronger", "family": "beta", "a": 2, "b": 18, "rationale": "Strength alternative"}],
            "evidence": {"prior": [evidence("external", "prior.md", "external-cohort")],
                         "validation": [{**evidence("check", "validation.json", "independent-cohort"),
                                         "counts": {"successes": 1, "trials": 10}}],
                         "likelihood": [evidence("panel", "likelihood.json", "reserved-panel"),
                                        evidence("measurement", "domain.yaml", "protocol")]},
            "checks": {"predictive_trials": 20, "plausible_rate_range": [0, 1], "max_outside_mass": .1,
                       "min_validation_tail": .0001, "posterior_threshold": .1, "decision_probability": .95,
                       "material_mean_shift": .05}}
        self.protocol_file = "setup/priors/protocol.yaml"
        self.flush()
        self.config = fixtures.fixture_config()
        self.config["base_overrides"]["statistics"] = {"approach": "bayesian"}
        self.config["runtime"].update(mode="research", domain_config="domain.yaml")

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative, value):
        (self.root / relative).write_text(json.dumps(value, indent=2))

    def flush(self):
        self.write(self.protocol_file, self.protocol)

    def approved(self, candidate="cautious"):
        record = approve(self.root, self.protocol_file, candidate, "Reviewer", "Applicable and independent",
                         evidence_reviewed=True)
        path = write_record(self.root, "setup/priors/approved.json", record)
        return path, load_approved(self.root, path)

    def test_independent_evidence_checks_are_explicit_not_approval(self):
        with patch("labton.decisions.decision_client_for", side_effect=AssertionError("Offline")):
            report = check_protocol(self.root, self.protocol_file)
        self.assertEqual(report["status"], "checked_not_approved")
        self.assertEqual(set(report["eligible_candidates"]), {"broad", "cautious", "stronger"})
        cautious = report["candidates"][1]
        self.assertAlmostEqual(cautious["mean"], .1)
        self.assertEqual(cautious["concentration"], 10)
        self.assertIn("validation", cautious)
        with self.assertRaises(PriorError):
            approve(self.root, self.protocol_file, "cautious", "Reviewer", "Reason")

    def test_overlap_detected_through_content_units_or_lineage(self):
        original = deepcopy(self.protocol)
        for mode in ("same_file", "renamed_content", "unit", "missing_unit", "lineage"):
            with self.subTest(mode=mode):
                self.protocol = deepcopy(original)
                left = self.protocol["evidence"]["prior"][0]
                right = self.protocol["evidence"]["likelihood"][0]
                if mode == "same_file":
                    left["file"] = right["file"]
                elif mode == "renamed_content":
                    (self.root / "copy.json").write_bytes((self.root / "likelihood.json").read_bytes())
                    left["file"] = "copy.json"
                elif mode in {"unit", "missing_unit"}:
                    left["dataset_id"] = right["dataset_id"]
                    left["observation_ids"] = right["observation_ids"] if mode == "unit" else []
                else:
                    left["lineage_ids"] = right["lineage_ids"] = ["original-subject-12"]
                self.flush()
                with self.assertRaises(PriorError):
                    check_protocol(self.root, self.protocol_file)

    def test_disjoint_units_of_shared_dataset_require_explicit_ids(self):
        self.protocol["evidence"]["prior"][0]["dataset_id"] = "reserved-panel"
        self.flush()
        self.assertTrue(check_protocol(self.root, self.protocol_file)["eligible_candidates"])

    def test_validation_counts_are_file_backed_and_conflicting_prior_fails(self):
        self.protocol["evidence"]["validation"][0]["counts"]["successes"] = 2
        self.flush()
        with self.assertRaises(PriorError):
            check_protocol(self.root, self.protocol_file)
        self.protocol["evidence"]["validation"][0]["counts"]["successes"] = 1
        self.protocol["candidates"][2].update(a=10000, b=1)
        self.protocol["checks"].update(plausible_rate_range=[0, .5], max_outside_mass=.1)
        self.flush()
        bad = check_protocol(self.root, self.protocol_file)["candidates"][2]
        self.assertFalse(bad["passed"])
        self.assertGreater(bad["predictive_outside_mass"], .99)
        self.assertLess(bad["validation"][0]["predictive_tail"], .0001)
        with self.assertRaises(PriorError):
            approve(self.root, self.protocol_file, "stronger", "Reviewer", "Reason", evidence_reviewed=True)

    def test_changed_evidence_protocol_or_approval_requires_new_review(self):
        path, record = self.approved()
        self.assertEqual(record["selected_candidate"], "cautious")
        for name in ("prior.md", "validation.json", "likelihood.json", "domain.yaml", self.protocol_file, path):
            file = self.root / name
            original = file.read_bytes()
            with self.subTest(file=name):
                if name == path:
                    changed = json.loads(original)
                    changed["selected_candidate"] = "broad"
                    self.write(name, changed)
                else:
                    file.write_bytes(original + b"\n")
                with self.assertRaises(PriorError):
                    load_approved(self.root, path)
            file.write_bytes(original)
        with self.assertRaises(FileExistsError):
            write_record(self.root, path, {})
        with self.assertRaises(PriorError):
            write_record(self.root, "results/leak.json", {})

    def test_runtime_binds_actual_panel_and_protocol_and_rejects_seed_reuse(self):
        path, _ = self.approved()
        statistics = {"approach": "bayesian", "prior_records": {"run_false_alarms": path}}
        records = runtime_priors(self.root, self.config, statistics)
        self.assertEqual(records["run_false_alarms"]["selected_candidate"], "cautious")
        (self.root / path).unlink()
        self.protocol["evidence"]["prior"][0]["observation_ids"] = ["seed:0"]
        self.flush()
        path, _ = self.approved()
        with self.assertRaisesRegex(PriorError, "seed"):
            runtime_priors(self.root, self.config, statistics)
        (self.root / path).unlink()
        self.protocol["evidence"]["prior"][0]["observation_ids"] = ["independent"]
        self.protocol["evidence"]["likelihood"].pop()
        self.flush()
        self.approved()
        with self.assertRaisesRegex(PriorError, "domain protocol"):
            runtime_priors(self.root, self.config, statistics)

    def test_exact_posterior_and_sensitivity_use_each_likelihood_once(self):
        _, record = self.approved()
        result = posterior_sensitivity(2, 10, record)
        self.assertEqual(result["selected"]["posterior_beta"], [3, 17])
        self.assertAlmostEqual(result["selected"]["mean"], .15)
        self.assertEqual(result["likelihood_uses_per_fit"], 1)
        self.assertGreater(result["posterior_mean_range"], .05)
        self.assertTrue(result["sensitive"])
        # Separate repeat analyses keep the original prior, rather than compounding evidence.
        self.assertEqual(result, posterior_sensitivity(2, 10, record))
        self.assertEqual(posterior_sensitivity(0, 0, record)["status"], "no_likelihood_observations")
        for k, n in ((True, 1), (2, 1), (-1, 2)):
            with self.assertRaises(ConfigurationError):
                posterior_sensitivity(k, n, record)

    def test_decision_change_detected_and_priors_scoped_to_primary_target(self):
        self.protocol["checks"]["decision_probability"] = .7
        self.flush()
        _, record = self.approved()
        report = posterior_sensitivity(0, 2, record)
        self.assertTrue(report["threshold_decision_changed"])
        self.assertAlmostEqual(report["alternatives"][0]["probability_above_threshold"], .9 ** 3)
        row = {"status": "measured", "alpha": .1, "run_false_alarms": {"k": 0, "n": 2},
               "fault_recall": {"k": 1, "n": 2}, "by_family": {"x": {"k": 0, "n": 1}}}
        other = {**deepcopy(row), "alpha": .05}
        result = apply_priors({"status": "valid", "results": [row, other]}, {"run_false_alarms": record})
        self.assertIn("bayesian", result["results"][0]["run_false_alarms"])
        self.assertNotIn("bayesian", result["results"][0]["fault_recall"])
        self.assertNotIn("bayesian", result["results"][1]["run_false_alarms"])

    def test_proposal_is_prior_only_one_call_uncalibrated_and_never_approved(self):
        bodies = []
        def transport(method, endpoint, body):
            bodies.append(body)
            return {"model": "resolved-offline-model", "answers": {"prior_candidate":
                    {"choice": "cautious", "confidence": .99,
                     "probabilities": {"broad": .01, "cautious": .98, "stronger": .01}}},
                    "usage": {"input_tokens": 9, "output_tokens": 2}}
        with patch("labton.study.api_key", return_value=fixtures.FAKE_KEY):
            proposal = asyncio.run(suggest(self.root, self.protocol_file, self.config, "a-none", "specialist",
                                          live=True, transport=transport))
        self.assertEqual(len(bodies), 1)
        self.assertEqual(proposal["provider_post_requests"], 1)
        self.assertFalse(proposal["automatic_adoption"])
        self.assertIn("not_empirically_calibrated", proposal["confidence_status"])
        payload = json.dumps(bodies)
        self.assertIn("External prior-only cohort", payload)
        self.assertNotIn("VALIDATION_NOT_FOR_ELICITOR", payload)
        self.assertNotIn("confirmation", payload)
        self.assertNotIn("likelihood.json", payload)
        path = write_record(self.root, "setup/priors/proposal.json", proposal)
        with self.assertRaises(PriorError):
            load_approved(self.root, path)
        approved = approve(self.root, self.protocol_file, "broad", "Reviewer", "Prefer weaker assumptions",
                           evidence_reviewed=True, proposal_file=path)
        self.assertEqual(approved["selected_candidate"], "broad")
        self.assertEqual(approved["proposal"]["recommended_candidate"], "cautious")

    def test_explicit_live_and_bayesian_selection_are_required_without_requests(self):
        with patch("labton.decisions.decision_client_for", side_effect=AssertionError("No request")):
            with self.assertRaises(PriorError):
                asyncio.run(suggest(self.root, self.protocol_file, self.config, "a-none", "specialist"))
            self.config["base_overrides"]["statistics"]["approach"] = "frequentist"
            with self.assertRaises(PriorError):
                asyncio.run(suggest(self.root, self.protocol_file, self.config, "a-none", "specialist", live=True))

    def test_plans_freeze_review_hash_and_reject_unapproved_before_research(self):
        path, record = self.approved()
        statistics = self.config["base_overrides"]["statistics"]
        statistics["prior_records"] = {"run_false_alarms": path}
        plan = plans(fixtures.PROJECT, self.config, workspace=self.root)["a-none"]
        self.assertEqual(plan["configuration_snapshot"]["providers"]["prior_approvals"]["run_false_alarms"],
                         record["record_sha256"])
        self.assertEqual(plan["statistics"]["status"], "reviewed_prior_protocol_bound")
        (self.root / "mission").mkdir()
        (self.root / "mission/problem.md").write_text("An actual research mission")
        self.write("study.yaml", self.config)
        (self.root / "prior.md").write_text("Changed prior evidence")
        with patch("labton.study.api_key", side_effect=AssertionError("No credentials/provider before preflight")):
            with self.assertRaises(PriorError):
                asyncio.run(run_variant(fixtures.PROJECT, self.root, "a-none"))
        self.assertFalse((self.root / "trials").exists())

    def test_cli_offline_check_and_approval(self):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            status = main(["priors", "check", "--workspace", str(self.root), "--protocol", self.protocol_file])
        self.assertEqual(status, 0, errors.getvalue())
        self.assertEqual(json.loads(output.getvalue())["status"], "checked_not_approved")
        with redirect_stdout(io.StringIO()), redirect_stderr(errors):
            status = main(["priors", "approve", "--workspace", str(self.root), "--protocol", self.protocol_file,
                           "--candidate", "cautious", "--reviewer", "Reviewer", "--rationale", "Independent evidence",
                           "--evidence-reviewed", "--output", "setup/priors/cli-approved.json"])
        self.assertEqual(status, 0, errors.getvalue())
        self.assertEqual(load_approved(self.root, "setup/priors/cli-approved.json")["selected_candidate"], "cautious")

    def test_frozen_files_and_unsupported_modes_fail_closed(self):
        path, record = self.approved()
        verify_frozen_files(self.root, {"run_false_alarms": record})
        (self.root / "prior.md").write_text("Research observation that must not replace frozen evidence")
        with self.assertRaises(PriorError):
            verify_frozen_files(self.root, {"run_false_alarms": record})
        statistics = {"approach": "bayesian", "prior_records": {"run_false_alarms": path}}
        for mode in ("frequentist", "text_only", "unsupported_adapter"):
            with self.subTest(mode=mode), self.assertRaises(PriorError):
                config = deepcopy(self.config)
                settings = deepcopy(statistics)
                if mode == "frequentist":
                    settings["approach"] = mode
                elif mode == "text_only":
                    config["runtime"]["mode"] = mode
                else:
                    self.write("domain.yaml", {"adapter_kind": "other"})
                runtime_priors(self.root, config, settings)
        self.assertEqual(runtime_priors(self.root, self.config, {"approach": "frequentist"}), {})

    def test_existing_output_is_rejected_before_a_paid_suggestion(self):
        self.write("study.yaml", self.config)
        self.write("setup/priors/existing.json", {"do_not_overwrite": True})
        errors = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(errors), patch(
            "labton.priors.suggest", side_effect=AssertionError("No provider request for invalid output")
        ):
            status = main(["priors", "suggest", "--workspace", str(self.root), "--protocol", self.protocol_file,
                           "--variant", "a-none", "--provider", "specialist", "--live",
                           "--output", "setup/priors/existing.json"])
        self.assertEqual(status, 2)
        self.assertIn("cannot be overwritten", errors.getvalue())

    def test_labs_bind_separate_reviewed_priors_without_pooling(self):
        from labton.multi_lab import compile_multi_lab
        from test_multi_lab import config_for_tests
        path, record = self.approved()
        other_approval = approve(self.root, self.protocol_file, "broad", "Reviewer", "Compare a weaker prior",
                                 evidence_reviewed=True)
        other_path = write_record(self.root, "setup/priors/other-approved.json", other_approval)
        config = config_for_tests()
        config["runtime"].update(mode="research", domain_config="domain.yaml")
        config["base_overrides"]["statistics"] = {"approach": "bayesian", "prior_records": {"run_false_alarms": path}}
        other_variant = deepcopy(config["variants"][0])
        other_variant.update(id="other")
        other_variant["overrides"]["statistics"] = {"prior_records": {"run_false_alarms": other_path}}
        config["variants"].append(other_variant)
        config["multi_lab"]["labs"][1]["variant"] = "other"
        plan = compile_multi_lab(fixtures.PROJECT, config, workspace=self.root)
        lab_plans = [lab["plan"] for lab in plan["multi_lab"]["labs"]]
        hashes = [p["configuration_snapshot"]["providers"]["prior_approvals"]["run_false_alarms"] for p in lab_plans]
        self.assertEqual(hashes[0], record["record_sha256"])
        self.assertNotEqual(hashes[0], hashes[1])
        self.assertEqual(lab_plans[0]["statistics"]["prior_records"]["run_false_alarms"], path)
        self.assertEqual(lab_plans[1]["statistics"]["prior_records"]["run_false_alarms"], other_path)


if __name__ == "__main__":
    unittest.main()
