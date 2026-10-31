# Evidence, memory and user-run comparisons

Updated: 2026-10-26. The user chooses the lab design, communication, and other settings and will
run comparisons later. There is no automated lab-improvement, self-modification, or promotion loop.

## User control

Users may change settings between runs or during work. Record the effective configuration and
when a change takes effect; snapshots are historical records, not configuration locks. No style
or communication setting needs to pass an acceptance gate. The planner re-reads files
on each invocation; applying changes during live work remains a future runtime implementation.

When a runtime change affects an active task, finish, cancel, or reschedule that task explicitly
and record the user's selected boundary. Preserve previous knowledge exposure. Restricting later
sharing cannot erase an earlier read, and a mixed-setting run should be identified as such.

## Research evidence and verification

Record observable transitions: question → prediction and proposed action → actual invocation
and receipt → observation → revised hypothesis or scoped claim. Link actor, team, configuration,
input snapshot, resource use, and artifact hashes. Proposed actions and post-hoc explanations
remain distinguishable from executed tests and premeasurement predictions.

Domain adapters establish inputs, allowed actions, output validation, meaningful metrics, and
confirmation protocols. Qualify them with a reproducible baseline and known-valid/invalid cases.
Distinguish a scientific negative result from environment, execution, or contract failure.
Confirmation evaluates the candidate artifact and intended scope. Changes to a candidate or an
integration require fresh applicable checks; organizational settings remain the user's choice.

When statistical analysis is needed, the user chooses **frequentist p-value analysis** or
**Bayesian analysis**. The domain adapter supplies the appropriate protocol. Record the selected
approach, assumptions, effect/uncertainty, actual result artifacts, and explicit unavailable or
inconclusive outcomes. This also supports later user-run comparisons of lab approaches.
See [statistical_analysis.md](statistical_analysis.md) for the configuration and record contract.

## Three memory layers

| Layer | Purpose |
|---|---|
| Evidence archive | Immutable observations, receipts, candidates, failures, and lineage |
| Operational playbooks | Detailed scoped methods, conditions, diagnostics, contradictions, and revisions |
| Horizontal views | Recipient-filtered low/intermediate/high content and optional wisdom abstractions |

Wisdom is a view rather than the entire retained memory. Maintain source/access lineage and
actual-read history. Shared playbooks, prompts, caches, and decision calls can carry peer
information and must obey the current communication policy. Retaining useful findings does
not authorize the system to rewrite its lab design, prompts, tools, or model weights.

## Later comparisons run by the user

Keep every lab style and communication profile available. The user can choose a trial setup,
run it, inspect the results, and change settings. For controlled comparisons, offer records of:

- objective, comparator, inputs, model/tool/environment identities, and effective configuration;
- total budgets and actual costs, including meetings, decisions, children, retries, and failed tests;
- verified practical benefit, uncertainty, failure rates, elapsed time, and scope of reuse;
- what collaboration occurred and which mechanisms or representations were actually explored;
- initial knowledge, settings changes, and actual peer exposure.

The user may choose fresh contexts and matched budgets to isolate a factor. These are comparison
techniques, not system-enforced locks or prerequisites for using a preset. Useful tradeoffs and
inconclusive results remain visible. No automatic recommendation becomes an applied setting.

Decision tools can be assessed through their effect on work, including same-LLM calls and an
optional specialist. A semantic judgment/confidence is distinct from a calibrated prediction
of experimental gain. Predictive surrogates and training are not required by this skeleton.
