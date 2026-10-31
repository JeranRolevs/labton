# Labton 0.3.0 release notes

An optional multi-lab layer composes the same or different study variants into
separate labs. The user chooses inter-lab communication (none, low, intermediate,
high, optional wisdom or wisdom only), a conference or symposium, and the number
of research sequences. Histories continue by default; an explicit fresh-context
option remains available. Shared and per-lab budgets include meeting requests.

Initialize with labton init my-labs --template multi-lab, then use prepare, run or
visualize with --multi-lab. See the [configuration and workflow guide](MULTI_LAB.md).
Existing study.yaml files and single-lab commands remain compatible; add multi_lab
only when using this layer. Conferences present findings, while symposia add bounded
discussion rounds. All contributions obey the same inter-lab filters. Confirmation
waits until every research sequence and meeting ends, separately for each lab.
No automatic winner, lab redesign or extra sequence is introduced.

## 0.2.0 service configuration

This release uses configurable service protocols for generation and optional semantic
decisions. It supplies no provider account, service URL or default model selection.
The six lab designs, user-selected budgets, single-scientist sequences and local process
monitor remain available.

## Configuration changes

Existing workspaces need their study.yaml provider settings updated using
[the provider guide](PROVIDERS.md). Choose base_url, endpoint, model, authentication and
request_options explicitly. A service must implement the selected protocol; unsupported
protocols require another adapter. Placeholder .invalid URLs and YOUR_MODEL_ID values
are accepted for planning but rejected before a live request.

Every optional specialist must be declared under decision_providers. Choose chat_completions
or typed and then select its configured ID. New templates default to LLM-only decisions.
The optional 45-variant memory matrix includes explicit chat/typed specialist variants that
need their own configuration. Different accounts can use separate key environment variables.

Model listing is opt-in. Loopback HTTP and explicit unauthenticated endpoints are supported;
remote connections otherwise require HTTPS. Request options cannot replace identity,
messages, streaming or output bounds. Failed/uncertain requests and fallbacks retain the
shared budget and no-automatic-retry behavior. Provider bindings enter configuration IDs.
Decision usage is grouped by configured endpoint and reported in aggregate token columns.

## Release boundaries

Historical reviews, design archives, local audit records, private data, keys, generated
trials and full local Git backups are excluded from the public tree and distribution
artifacts. Preserve required dependency and licence notices. Run the starter synchronization,
offline tests, artifact checks and an installed-wheel smoke check before publishing.

Setup, tests, package builds, structural plans, visualizations and diagrams make no model
calls. Live connectivity checks and research runs remain explicit, separately budgeted actions.

## Licence and attribution

Labton remains under the [Academic Research License](../LICENSE), with unrestricted donations
allowed only under its stated conditions. Pioneertown B.V. is the copyright holder and
licensor; Goran Mitevski is the author. [Full licensing summary](../LICENSING.md).
