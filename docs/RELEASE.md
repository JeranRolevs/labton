# Labtune 0.5.0 release notes

The product, repository, Python distribution, import namespace and command are now named
**Labtune** / `labtune`. Repository links point to
[JeranRolevs/labtune](https://github.com/JeranRolevs/labtune). The dashboard, diagrams, starter
workspaces, CI and licence branding use the new name. The licence's eligibility, research,
funding and company-lab restrictions continue under the renamed licence identifier.

New workspace examples use `LABTUNE_API_KEY` and `LABTUNE_DECISION_API_KEY`. Existing studies
continue to use the environment-variable names explicitly declared in their configuration.
Existing workspace launchers need their import updated to `labtune.cli`; the new CLI can
also operate on an existing workspace directly. See [migration instructions](MIGRATION.md).

## 0.4.1 geographic licensing

Labtune Academic Research License 2.0 limits free independent noncommercial academic research
to qualifying public or nonprofit educational institutions genuinely based in World Bank
low-income or lower-middle-income economies and their authorized users. Company labs,
corporate research proxies and commissioned company work remain excluded. Unrestricted
donations must meet the licence's conditions. Upper-middle-income, high-income and
unclassified economies are outside the free permission.

Other use requires a separate written licence from Pioneertown B.V. through Goran Mitevski:
[goran@pioneertown.ai](mailto:goran@pioneertown.ai).
Version 2.0 does not purport to revoke or rewrite permissions granted for
earlier copies. Package metadata, notices and starter workspaces carry the new terms.
See [LICENSE](../LICENSE) and [the licensing summary](../LICENSING.md).

## 0.4.0 reviewed model-assisted priors

Bayesian binomial analyses can optionally use a decision model to recommend from explicit
Beta prior candidates. Prior-only evidence goes to the model; independent validation and
likelihood outcomes stay outside its context. Local checks cover known evidence overlap,
prior predictive implications and independent validation counts. Explicit user review is
required before adoption, and review hashes bind the protocol, evidence and model proposal.

The memory adapter reports exact posterior sensitivity across declared alternatives for
approved primary run-rate targets. Priors remain fixed across research sequences; protected
confirmation remains separate. Unsupported adapters reject this option. Existing manual priors
and frequentist configurations remain compatible. Install the optional `bayesian` extra for
local diagnostics; `memory` already supplies its numeric dependencies. No setup or planning
requests are introduced. See [the workflow and limitations](BAYESIAN_PRIORS.md).

## 0.3.0 multi-lab layer

An optional multi-lab layer composes the same or different study variants into
separate labs. The user chooses inter-lab communication (none, low, intermediate,
high, optional wisdom or wisdom only), a conference or symposium, and the number
of research sequences. Histories continue by default; an explicit fresh-context
option remains available. Shared and per-lab budgets include meeting requests.

Initialize with labtune init my-labs --template multi-lab, then use prepare, run or
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

Review history, tags and release assets before making the repository public: earlier commits
contain the broader version 1.0 licence. Updating the current licence does not change those
historical copies. A fresh public snapshot can avoid newly distributing those earlier
versions; it does not revoke permissions already granted to earlier recipients.

Setup, tests, package builds, structural plans, visualizations and diagrams make no model
calls. Live connectivity checks and research runs remain explicit, separately budgeted actions.

## Licence and attribution

Labtune uses the [Academic Research License 2.0](../LICENSE), with free use limited to qualifying
institutions in World Bank low-income or lower-middle-income economies and unrestricted
donations allowed only under its stated conditions. Pioneertown B.V. is the copyright holder and
licensor; Goran Mitevski is the author. [Full licensing summary](../LICENSING.md).
