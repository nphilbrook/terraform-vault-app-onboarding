# Agent Instructions — Testing Module Changes on HCP Terraform

This document describes how an AI agent should test changes to this Terraform module using the HCP Terraform API.

## General Rules

- Commit and push code changes to branches without asking for confirmation. Do not wait for approval before committing or pushing.
- Every module change must be tested against **all** example workspaces before merging.

## Overview

This repository is a Terraform module that creates Vault AWS auth backend roles with optional KV policies. Each subdirectory under `examples/` is a self-contained Terraform root module that exercises a specific use case. Each example has a dedicated HCP Terraform workspace that uses `working_directory` to scope runs to that example.

## Example Workspaces

Each example directory maps to a workspace. The workspaces are managed as `tfe_workspace` resources in the `hcp-tf-control` repository (`aws_hvd_vault_onboarding.tf`).

| Example directory | Workspace name | Workspace ID |
|---|---|---|
| `examples/basic` | `vault-onboarding-basic` | `ws-pidXJL85KawYBFAJ` |
| `examples/with-kv-policy` | `vault-onboarding-with-kv-policy` | `ws-aNjJT2MRGWZSSw5y` |

> **After the hcp-tf-control workspaces are created**, update the workspace IDs in this table.

Examples are self-contained — all variable values are hardcoded in each example's `main.tf`. No workspace variables need to be set via the API.

## Prerequisites

| Item | Value |
|---|---|
| HCP Terraform API base | `https://app.terraform.io/api/v2` |
| Organization | `philbrook` |
| GitHub App Installation ID | `ghain-ieieBWKoaGhWE3rE` |
| Repository identifier | `nphilbrook/terraform-vault-app-onboarding` |
| API token file | `TOKEN` (repo root) |

Load the API token:

```sh
export TFE_TOKEN=$(cat TOKEN)
```

All API requests require the header `Authorization: Bearer $TFE_TOKEN` and `Content-Type: application/vnd.api+json`.

## Testing Workflow

### 1. Create a branch and push changes

```sh
git checkout -b <branch-name>
# ... make changes ...
git add -A && git commit -m "<description>"
git push -u origin <branch-name>
```

### 2. Point each workspace at the branch

For **every** workspace listed in the Example Workspaces table, update the VCS integration to track your branch:

```
PATCH /workspaces/<workspace-id>
```

```json
{
  "data": {
    "type": "workspaces",
    "attributes": {
      "vcs-repo": {
        "identifier": "nphilbrook/terraform-vault-app-onboarding",
        "github-app-installation-id": "ghain-ieieBWKoaGhWE3rE",
        "branch": "<branch-name>"
      }
    }
  }
}
```

### 3. Trigger a plan on each workspace

For each workspace, check for existing runs and trigger a plan if none is queued:

```
GET /workspaces/<workspace-id>/runs
```

```
POST /runs
```

```json
{
  "data": {
    "type": "runs",
    "attributes": { "message": "Triggered via agent" },
    "relationships": {
      "workspace": {
        "data": { "id": "<workspace-id>", "type": "workspaces" }
      }
    }
  }
}
```

### 4. Poll and apply each run

Poll the run status until it reaches a terminal or confirmable state:

```
GET /runs/<run-id>
```

- **Terminal states**: `planned_and_finished`, `applied`, `errored`, `discarded`, `canceled`, `force_canceled`
- **Confirmable states** (apply the run): `planned`, `cost_estimated`, `policy_checked`, `post_plan_completed`

To apply:

```
POST /runs/<run-id>/actions/apply
```

```json
{ "comment": "Applied via agent" }
```

Review the plan output before applying. If the plan shows unexpected changes, investigate before confirming. **All** example workspaces must apply successfully before the change is considered tested.

### 5. Clean up — reset workspace branches

After testing, reset **every** workspace's VCS integration back to the default branch:

```
PATCH /workspaces/<workspace-id>
```

```json
{
  "data": {
    "type": "workspaces",
    "attributes": {
      "vcs-repo": {
        "identifier": "nphilbrook/terraform-vault-app-onboarding",
        "github-app-installation-id": "ghain-ieieBWKoaGhWE3rE",
        "branch": "",
        "default-branch": true
      }
    }
  }
}
```

## Adding a New Use Case

When adding a new use case to the module:

1. Create a new directory under `examples/` (e.g., `examples/my-new-case`) with a self-contained `main.tf` and `versions.tf`.
2. Add a corresponding `tfe_workspace` resource in the `hcp-tf-control` repository's `aws_hvd_vault_onboarding.tf` file, with `working_directory` set to the new example path.
3. Apply the `hcp-tf-control` workspace to create the new workspace.
4. Update the **Example Workspaces** table in this file with the new workspace name and ID.

## Reference

The `scripts/` directory contains Python scripts that demonstrate the full API patterns:

- **create_workspace.py** — creates a VCS-backed workspace, sets variables, triggers a run, and polls to completion.
- **update_workspace.py** — updates variables on an existing workspace and triggers a run.
- **delete_workspace.py** — triggers a destroy run, polls to completion, then deletes the workspace.

These scripts read the token from `TFE_TOKEN` environment variable and can be used as executable references for API call structure, error handling, and polling logic.
