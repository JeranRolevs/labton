"""Exact Beta/binomial diagnostics; no model confidence enters these calculations."""
from __future__ import annotations

import math
from fractions import Fraction

from .config import ConfigurationError


def distributions():
    try:
        from scipy.stats import beta, betabinom
    except ImportError:
        raise ConfigurationError("Prior diagnostics require the bayesian extra: pip install 'labton[bayesian]'.") from None
    return beta, betabinom


def finite(value):
    result = float(value)
    if not math.isfinite(result):
        raise ConfigurationError("Prior diagnostic is numerically undefined; revise the protocol before review.")
    return result


def prior_checks(candidates, checks, validation):
    beta, betabinom = distributions()
    horizon = checks["predictive_trials"]
    lower, upper = checks["plausible_rate_range"]
    first = math.ceil(Fraction(str(lower)) * horizon)
    last = math.floor(Fraction(str(upper)) * horizon)
    rows = []
    for candidate in candidates:
        a, b = candidate["a"], candidate["b"]
        outside = finite(betabinom.cdf(first - 1, horizon, a, b)
                         + betabinom.sf(last, horizon, a, b))
        validation_rows = []
        for source in validation:
            k, n = source["counts"]["successes"], source["counts"]["trials"]
            # Conservative, doubled smaller inclusive tail, not a calibrated model score.
            tail = min(1., 2 * min(finite(betabinom.cdf(k, n, a, b)),
                                   finite(betabinom.sf(k - 1, n, a, b))))
            validation_rows.append({"evidence_id": source["id"], "successes": k, "trials": n,
                                    "predictive_tail": tail,
                                    "passed": tail >= checks["min_validation_tail"]})
        rows.append({"id": candidate["id"], "family": "beta", "a": a, "b": b,
                     "mean": a / (a + b), "concentration": a + b,
                     "interval95": [finite(beta.ppf(.025, a, b)), finite(beta.ppf(.975, a, b))],
                     "predictive_trials": horizon, "predictive_outside_mass": outside,
                     "validation": validation_rows,
                     "passed": outside <= checks["max_outside_mass"] and all(r["passed"] for r in validation_rows)})
    return rows


def posterior_sensitivity(k, n, record):
    """Fit each prior separately to the same counts, never recycle one posterior as a prior."""
    if (isinstance(k, bool) or isinstance(n, bool) or not isinstance(k, int)
            or not isinstance(n, int) or not 0 <= k <= n):
        raise ConfigurationError("Binomial sensitivity requires integer counts with 0 <= successes <= trials.")
    beta, _ = distributions()
    checks = record["checks"]
    rows = []
    for candidate in record["candidates"]:
        a, b = candidate["a"] + k, candidate["b"] + n - k
        probability = finite(beta.sf(checks["posterior_threshold"], a, b))
        rows.append({"id": candidate["id"], "prior_beta": [candidate["a"], candidate["b"]],
                     "posterior_beta": [a, b], "mean": a / (a + b),
                     "credible95": [finite(beta.ppf(.025, a, b)), finite(beta.ppf(.975, a, b))],
                     "probability_above_threshold": probability,
                     "threshold_criterion_met": probability >= checks["decision_probability"]})
    span = max(r["mean"] for r in rows) - min(r["mean"] for r in rows)
    changed = len({r["threshold_criterion_met"] for r in rows}) > 1
    return {"status": "no_likelihood_observations" if n == 0 else "completed",
            "selected": next(r for r in rows if r["id"] == record["selected_candidate"]),
            "alternatives": rows, "posterior_mean_range": span, "threshold_decision_changed": changed,
            "sensitive": span > checks["material_mean_shift"] or changed,
            "checks": checks, "likelihood_uses_per_fit": 1 if n else 0,
            "scope": "Sensitivity to the declared candidate set only; this does not establish prior correctness."}
