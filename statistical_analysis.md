# User-selected statistical approach

When statistical analysis is needed, the user chooses **frequentist analysis with p-values**
or **Bayesian analysis**. This choice is independent of lab style, sharing, and decision backend.
It applies to applicable mission experiments and confirmation, and can also be used for the
user's later comparisons of organizational approaches.

## Selection

Set the current configuration:

```yaml
statistics:
  approach: frequentist  # frequentist | bayesian
```

Or inspect an override from the Labton directory:

```bash
labton --project . plan --statistics bayesian
```

The editable example/default is `frequentist`; it is not a claim of superiority. Each plan
records the selected approach in its configuration fingerprint. The user can change it without
an acceptance gate. As with other settings, future runtime changes record their effective
boundary; previous analyses retain the method and inputs actually used.

## Domain-specific protocol

Selecting a family does not select a universal test or model. Before analyzing relevant data,
the domain adapter supplies an identified protocol and records the question, measurement unit,
comparator, effect definition, sampling/replicate design, assumptions, and stopping rules.
The user can review or revise it. It must preserve the chosen statistical family rather than
silently switching after inspecting the result. A changed protocol creates a recorded analysis.

| Approach | Protocol and result contents |
|---|---|
| Frequentist | Suitable test and assumptions, null/alternative, direction, alpha if making a threshold decision, sample sizes, effect estimate, uncertainty interval, test statistic and p-value; account for multiple comparisons and repeated looks when applicable |
| Bayesian | Likelihood/model, explicit priors and sensitivity checks, posterior/effect summaries, credible intervals or stated probabilities, relevant model diagnostics; Bayes factors only when the protocol defines and supports them |

Neither alpha nor a posterior probability threshold is imposed by the skeleton. Protocol
templates leave them unset. Statistical evidence accompanies practical effect size, uncertainty,
cost, and the mission's usefulness criteria. A p-value is not the probability that the null
hypothesis is true and is not a measure of effect size.

Bayesian protocols include checks appropriate to the model and inference method. Prior and
posterior predictive checks can help assess the model's implications against relevant data
features.
Confidence intervals and credible intervals keep their distinct labels and interpretations.

## Evidence and implementation boundary

Every evaluation receipt has a `statistics` assessment containing the selected approach,
status, protocol reference, result references, and reason where appropriate:

- `not_required`: this investigation does not need statistical inference; record why.
- `not_run`: an applicable analysis has not been executed; record why.
- `unsupported`: the adapter cannot perform the selected analysis; record why.
- `completed`: actual analysis exists, with protocol and result references.
- `inconclusive`: actual analysis exists but does not settle the relevant question; retain it.

Exact-verifier tasks do not acquire unnecessary significance tests. An unavailable analysis
does not become a completed result or trigger a silent switch to the other family. P-values,
posterior probabilities, and intervals come from the identified evaluator/analysis tools,
not from an LLM's asserted confidence or a decision-model judgment. Future runtime validation checks
method compatibility, actual artifacts, assumptions and diagnostics; schemas only check shape.

The current skeleton resolves and records the policy and defines the evaluator interface.
It does not execute tests, sample posteriors, select a numeric library, or add dependencies.
The two [protocol templates](templates/statistics/README.md) are draft planning artifacts with
unset methods/parameters. They contain no measured results.
