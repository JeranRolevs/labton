# Labtune implementation boundary

Implement Labtune independently from the user's requirements and the code in this repository.
Do not copy, adapt, vendor or import implementation code, prompts, skills or templates from
unrelated projects or the surrounding historical workspace. Do not delegate execution to a
parent project, its CLI, modules or containers. If provenance is uncertain, retain the evidence
locally and resolve the specific overlap; renaming is not evidence of independence.

Build from this repository's pyproject.toml. Keep Labtune installable outside its development
workspace. Use declared general-purpose dependencies and preserve their required notices.

The user chooses lab styles, models, communication, statistics, delegation and budgets.
Do not add automated organizational improvement, silent model selection or budget increases.
Setup, tests, packaging, planning and diagram rendering must not make paid provider calls.
Credentials, private seed panels, trials and research results stay outside Git and packages.

Keep starter resources synchronized with tools/sync_starter.py. All diagrams use
diagrams/specs.py; regenerate with diagrams/render_flowcharts.py. Local archives, historical
reviews and audit records are intentionally ignored and must not enter a public export.

Labtune uses the Labtune Academic Research License 2.0. Free use is limited to qualifying
academic institutions in World Bank low-income or lower-middle-income economies and their
authorized users for independent noncommercial research. Other use requires separate written
permission through Goran Mitevski, goran@pioneertown.ai, on behalf of Pioneertown B.V.
Company labs, corporate research proxies and commissioned company work are excluded.
Company donations must be unrestricted, without control or privileged research/IP rights.
Preserve LICENSE and LICENSING.md in distributions and starter workspaces, including the
Pioneertown B.V. copyright/licensor notice and Goran Mitevski author credit. Do not change
licensing terms, commit, push or publish without user authorization.
