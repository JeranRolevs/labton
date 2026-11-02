# Reviewed, model-assisted Bayesian priors

When the user chooses Bayesian analysis, a named decision model can **recommend a prior**.
It cannot approve it. Labtune checks declared evidence separation and numerical implications,
then requires an explicit user review before the scientific adapter uses the prior.
The initial executable implementation covers **Beta priors for binomial rates**. It does not
generate priors for arbitrary likelihoods. The same workflow works with either generic
decision adapter; it does not require a particular service or change the lab's other models.

Install `labtune[bayesian]` for the local SciPy calculations (`labtune[memory]` also supplies SciPy).
Copy [the draft protocol](../templates/statistics/prior-elicitation.yaml) into
`setup/priors/protocol.yaml` in your workspace and fill it with actual evidence and assumptions.
Setup, planning, checks and approval make no model requests. Proposals, approvals and evidence
remain local; `setup/` is ignored by Git.

## Define the parameter and its evidence

State the parameter, population, unit of observation and success definition. Provide at least
three distinct candidate Beta distributions with explicit `a`, `b` and rationales. Include
meaningful alternatives with weaker information and different locations/strengths, rather than
near duplicates. The decision model chooses from these candidates. Its reported confidence
and option probabilities are uncalibrated judgments: they never set Beta parameters,
concentration, observation counts or posterior probabilities.

Each evidence entry identifies a local file, dataset, observation IDs, data lineage IDs and
relevance/limitations. Keep three roles separate:

- `prior`: external evidence extracts used to justify candidates and sent to the decision model.
- `validation`: independent relevant binomial counts used for local prior predictive checks.
  The referenced JSON must contain `successes` and `trials` matching the protocol entry.
- `likelihood`: the data and measurement protocol reserved for subsequent likelihood evaluation.
  These files and validation outcomes are excluded from the model's elicitation context.

Use stable dataset/observation IDs across copies and transformations. An observation ID is
scoped to its dataset; a lineage ID identifies the same underlying observations or their
derivatives across datasets. A shared study name alone is not an observation lineage.
The checker rejects shared paths, identical content hashes, intersecting lineage IDs, and
overlapping observations within a dataset across roles. A dataset shared across roles without
complete observation IDs is rejected because independence is unresolved. Disjoint partitions
still require a reviewer to assess dependence and transportability. Hashes and declared IDs
cannot detect undeclared aliases, inaccurate metadata, hidden data dependence or contamination
in a model's training data. Passing checks does not establish correctness.

Never use the current research outputs, their summaries or a previous posterior as independent
prior evidence for the same likelihood observations. If prior and likelihood evidence overlap,
either remove the overlap or design a supported joint likelihood/hierarchical analysis; Labtune
does not silently discount or reuse the evidence. Validation observations used to assess or
select a prior are also excluded from the subsequent likelihood.

## Suggest, check and review

In `study.yaml`, choose `statistics.approach: bayesian` in the base or selected variant overrides.
Declare the desired model under `decision_providers` as described in
[the decision provider guide](DECISION_PROVIDERS.md). The elicitor need not be the lab's active
decision specialist. A request uses a fresh prior-only context, exactly one provider request,
the smaller of the provider timeout and the selected wall-time cap, and no retries.
This is a separate, explicit elicitation budget; it is not taken silently from a research run.

```bash
labtune priors check --workspace /path/to/lab --protocol setup/priors/protocol.yaml

# Optional: one paid request to the explicitly selected provider.
labtune priors suggest --workspace /path/to/lab --protocol setup/priors/protocol.yaml \
  --variant single --provider specialist --live --max-wall-seconds 30 \
  --output setup/priors/proposal-1.json

labtune priors approve --workspace /path/to/lab --protocol setup/priors/protocol.yaml \
  --candidate cautious --reviewer "Researcher name" \
  --rationale "Explain evidence relevance, independence and the chosen assumptions" \
  --evidence-reviewed --proposal setup/priors/proposal-1.json \
  --output setup/priors/approved-1.json
```

`--proposal` is optional: manually elicited priors can use exactly the same checks and review.
The reviewer may select a different passing candidate from the model's recommendation, with
a recorded rationale. A proposal alone is never accepted as a runtime prior. Files are created
without overwriting earlier records. Reviewer names are supplied labels, not authenticated
identities; hashes detect changes, not malicious replacement by someone with filesystem access.

The local check records the SciPy version and reports the prior mean, concentration `a+b`, 95% prior interval, and the exact
Beta-binomial predictive probability of a future observed rate falling outside the declared
plausible range at the declared trial count. It also reports the doubled smaller inclusive
predictive tail for each independent validation count, capped at one. This is a conservative
conflict diagnostic, not a calibrated measure of model trustworthiness. Declare all cutoffs
before inspecting the likelihood. A selected candidate must pass the declared checks; failed
alternatives stay in the sensitivity set. Changing evidence, candidates or checks requires a
new reviewed version. A changed numeric backend or changed diagnostic results also requires
review. Do not tune checks repeatedly until an attractive prior passes.

## Use approved priors and inspect sensitivity

Set workspace-relative approval paths in the study's base or variant overrides:

```yaml
statistics:
  approach: bayesian
  prior_records:
    run_false_alarms: setup/priors/approved-1.json
```

Each configured target has its own protocol and approval. In a multi-lab study, variants can
reference the same approval for a shared protocol, or different approved assumptions. Reviews
bind to the plan fingerprint. Runs preflight them before research model calls; changed evidence,
protocols, proposals or approvals require a new review/plan. Priors stay fixed across research
sequences and meetings; agents cannot elicit or approve a replacement using observed results.

The memory adapter currently supports `run_false_alarms`, `fault_recall`, and
`benign_recurrence_alarm_runs` for its **primary alpha = 0.1**, with
`observation_unit: independent_run`. Their meanings depend on the fixed horizon, synthetic
population, policy and measurement protocol. Review that a prior is applicable to the policies
being considered; it is not automatically transferable across policy searches. Bind both the
actual `mission/memory/private_splits.json` and domain configuration file as likelihood evidence.
For seed-based prior or validation evidence use observation IDs `seed:<integer>` so the runtime
can check them against **all** reserved seed panels, including calibration and confirmation.
Domain changes invalidate approval, and evaluator source changes require normal requalification.
Unconfigured metrics, family subgroups and other alpha targets retain counts without borrowing
a prior from a different parameter. Other adapters reject this option until they implement it.

Each measured primary result reports the selected posterior and all declared alternatives:
Beta(`a + successes`, `b + trials - successes`), posterior means and 95% credible intervals,
probability above the user-declared rate threshold, and whether the declared probability criterion
is met. Labtune flags a sensitivity result when decisions differ or the posterior mean range
exceeds the declared material shift. Each fit uses the counts **once** with its original prior;
fits are separate, with no pooling of alternative posteriors or accumulation across sequences.
No extra experiments or provider requests are needed. With zero trials, results are explicitly
labelled as having no likelihood observations. Sensitivity covers the tested alternatives only.

Development posteriors are exploratory, particularly after adaptive policy selection. Protected
confirmation uses its own disjoint likelihood panel and the original approved prior; confirmation
results remain withheld from research agents. Model elicitation does not establish likelihood
adequacy, independence, external validity or a valid optional-stopping/comparison protocol.

Existing manual `protocol.bayesian_prior: [a,b]` remains available when no `prior_records` are
configured. That legacy path does not supply these evidence checks, review or sensitivity
reports. Frequentist runs do not invoke prior elicitation.
