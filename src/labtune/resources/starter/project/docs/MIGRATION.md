# Move an existing workspace to Labtune

The product formerly named Labton is now **Labtune**. From version 0.5.0, the Python
distribution, import namespace and command are all `labtune`. The repository is
[JeranRolevs/labtune](https://github.com/JeranRolevs/labtune).

## Install and use the renamed package

From a checkout of the renamed repository:

```bash
python3 -m pip install -e .
labtune --help
```

Or install a built wheel, adding the research extras when needed. Imports in application
code use `labtune` in place of `labton`. The previous command and import namespace are
not provided by this distribution; an independently installed old package is separate.

Existing workspace folders can keep their current names. To use one directly:

```bash
labtune --project /path/to/my-lab study prepare --workspace /path/to/my-lab
labtune --project /path/to/my-lab study visualize --workspace /path/to/my-lab --variant YOUR_VARIANT
```

In an existing workspace's `lab.py`, update the import to:

```python
from labtune.cli import main
```

Newly initialized workspaces already contain this import. Preparation and visualization
make no model requests. Configurations, private seed panels, results and approvals belong
to the workspace; reinitializing the directory is unnecessary.

## Credentials and recorded research

New starter configurations name `LABTUNE_API_KEY` and `LABTUNE_DECISION_API_KEY`.
An existing study still reads exactly the variable named by each provider's `api_key_env`,
including custom or previous names. Update both the configuration and private `.env` only
if you choose to rename them; no fallback key or provider is selected automatically.

Saved trials and exported snapshots retain the names and configuration identities they
recorded. New package code produces a new configuration identity. Regenerate structural
plans with `prepare`. For the memory adapter, repeat the offline `qualify` step because
the trusted evaluator's source hash changed. Prior approvals are checked against their
recorded protocol and evidence as usual; changed evidence requires a new review.

When updating licence/notices in an existing workspace, copy `LICENSE` and `LICENSING.md`
from the current checkout or a newly initialized temporary workspace. The custom licence
identifier is now `LicenseRef-Labtune-Academic-Research-2.0`; the geographic and institutional
eligibility conditions, ownership and author credit remain in the full terms. Updating
copies does not rewrite permissions previously granted for older material.
