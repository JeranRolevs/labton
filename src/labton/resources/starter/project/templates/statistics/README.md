# Statistical protocol templates

Use [frequentist.yaml](frequentist.yaml) or [bayesian.yaml](bayesian.yaml) to draft the applicable
domain protocol. These are marked templates with unset methods/parameters. They are not
executable analyses or validated protocols. No fixed test, prior, significance threshold,
posterior threshold, or numeric backend is mandated by the skeleton.

The domain adapter will bind an actual protocol and result artifacts to an evaluation receipt.
The optional [prior elicitation draft](prior-elicitation.yaml) and
[reviewed prior workflow](../../docs/BAYESIAN_PRIORS.md) support executable Beta/binomial checks,
explicit review, and runtime sensitivity analysis. Fill the draft with actual evidence before use.
Keep sample/replicate identities, data provenance, effect definitions, assumptions, stopping
rules, and analysis changes traceable. See [the statistical contract](https://github.com/JeranRolevs/labton/blob/main/statistical_analysis.md).
