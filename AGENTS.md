# Agent Instructions — Testing Module Changes on HCP Terraform

This document describes how an AI agent should test changes to this Terraform module using the HCP Terraform API.

## Overview

This repository is a Terraform module that creates Vault AWS auth backend roles with optional KV policies. Changes must be tested end-to-end on HCP Terraform before merging.

## Prerequisites

| Item | Value |
|---|---|
| HCP Terraform API base | `https://app.terraform.io/api/v2` |
| Organization | `philbrook` |
| Test workspace ID | `ws-AcrGvhSgvqEkdMNR` |
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

### 2. Point the workspace VCS integration at the branch

Update the workspace so it tracks your branch instead of the default branch:

```
PATCH /workspaces/ws-AcrGvhSgvqEkdMNR
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

### 3. Set workspace variables

List existing variables:

```
GET /workspaces/ws-AcrGvhSgvqEkdMNR/vars
```

Create or update variables as needed. At minimum the module requires:

| Variable | Category | HCL | Example value | Required |
|---|---|---|---|---|
| `name` | `terraform` | `false` | `my-test-role` | **yes** |
| `bound_iam_instance_profile_arns` | `terraform` | `true` | `["arn:aws:iam::instance-profile/example"]` | at least one `bound_*` |
| `create_kv` | `terraform` | `true` | `true` | no |
| `kv_path` | `terraform` | `false` | `my-test-role` | when `create_kv = true` |
| `backend` | `terraform` | `false` | `aws` | no (default `aws`) |
| `token_policies` | `terraform` | `true` | `["default"]` | no |

To create a variable:

```
POST /workspaces/ws-AcrGvhSgvqEkdMNR/vars
```

```json
{
  "data": {
    "type": "vars",
    "attributes": {
      "key": "<key>",
      "value": "<value>",
      "category": "terraform",
      "hcl": false,
      "sensitive": false,
      "description": ""
    },
    "relationships": {
      "workspace": {
        "data": { "id": "ws-AcrGvhSgvqEkdMNR", "type": "workspaces" }
      }
    }
  }
}
```

To update an existing variable (use the variable ID from the list response):

```
PATCH /workspaces/ws-AcrGvhSgvqEkdMNR/vars/<var-id>
```

### 4. Trigger a plan

After pushing to the branch the workspace may auto-trigger a run. Check for existing runs first:

```
GET /workspaces/ws-AcrGvhSgvqEkdMNR/runs
```

If no run is queued, trigger one manually:

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
        "data": { "id": "ws-AcrGvhSgvqEkdMNR", "type": "workspaces" }
      }
    }
  }
}
```

### 5. Poll the run and apply

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

Review the plan output before applying. If the plan shows unexpected changes, investigate before confirming.

### 6. Clean up — reset the workspace branch

After testing, reset the workspace VCS integration back to the default branch:

```
PATCH /workspaces/ws-AcrGvhSgvqEkdMNR
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

If you created test infrastructure, run a destroy before resetting the branch:

```
POST /runs
```

```json
{
  "data": {
    "type": "runs",
    "attributes": {
      "is-destroy": true,
      "message": "Destroy via agent"
    },
    "relationships": {
      "workspace": {
        "data": { "id": "ws-AcrGvhSgvqEkdMNR", "type": "workspaces" }
      }
    }
  }
}
```

Poll and apply the destroy run before resetting the branch.

## Reference

The `scripts/` directory contains Python scripts that demonstrate the full API patterns:

- **create_workspace.py** — creates a VCS-backed workspace, sets variables, triggers a run, and polls to completion.
- **update_workspace.py** — updates variables on an existing workspace and triggers a run.
- **delete_workspace.py** — triggers a destroy run, polls to completion, then deletes the workspace.

These scripts read the token from `TFE_TOKEN` environment variable and can be used as executable references for API call structure, error handling, and polling logic.
