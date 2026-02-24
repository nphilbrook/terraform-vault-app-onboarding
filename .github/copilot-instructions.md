# Agent Instructions — Testing Module Changes with HCP Terraform

This document describes how an AI agent should test changes to this Terraform module.

## General Rules

- Commit and push code changes to branches without asking for confirmation. Do not wait for approval before committing or pushing.
- Every module change must be tested against **all** examples before merging.

## Overview

This repository is a Terraform module that creates Vault AWS auth backend roles with optional KV policies. Each subdirectory under `examples/` is a self-contained Terraform root module that exercises a specific use case. Each example has a `cloud` backend block that stores state in the **AWS Vault LZs** project in HCP Terraform.

## Examples

| Example directory | Workspace name |
|---|---|
| `examples/basic` | `vault-onboarding-basic` |
| `examples/with-kv-policy` | `vault-onboarding-with-kv-policy` |

Examples are self-contained — all variable values are hardcoded in each example's `main.tf`. No workspace variables need to be set.

## Prerequisites

| Item | Value |
|---|---|
| HCP Terraform organization | `philbrook` |
| HCP Terraform project | `AWS Vault LZs` |
| API token file | `TOKEN` (repo root) |

Set the HCP Terraform API token as an environment variable so that Terraform can authenticate:

```sh
export TF_TOKEN_app_terraform_io=$(cat TOKEN)
```

**IMPORTANT:** You **must** set `TF_TOKEN_app_terraform_io` to the contents of the `TOKEN` file before running any Terraform commands. This is required for `terraform init` to authenticate with the HCP Terraform backend.

## Testing Workflow

### 1. Create a branch and push changes

```sh
git checkout -b <branch-name>
# ... make changes ...
git add -A && git commit -m "<description>"
git push -u origin <branch-name>
```

### 2. Test each example

For **every** example directory, run the full Terraform workflow:

```sh
export TF_TOKEN_app_terraform_io=$(cat TOKEN)

cd examples/<example-name>
terraform init
terraform plan
```

Review the plan output. If the plan shows unexpected changes, investigate before proceeding.

```sh
terraform apply -auto-approve
```

**All** examples must apply successfully before the change is considered tested.

### 3. Clean up (if needed)

If you need to tear down resources created during testing:

```sh
cd examples/<example-name>
terraform destroy -auto-approve
```

## Adding a New Use Case

When adding a new use case to the module:

1. Create a new directory under `examples/` (e.g., `examples/my-new-case`) with these files (per the [Terraform style guide](https://developer.hashicorp.com/terraform/language/style#file-names)):
   - `main.tf` — module call and outputs
   - `terraform.tf` — `required_version` and `required_providers`
   - `backend.tf` — `cloud` backend block (see below)
   - `providers.tf` — provider configuration
2. Include a `cloud` backend block in `backend.tf` pointing to the **AWS Vault LZs** project with a unique workspace name:
   ```hcl
   terraform {
     cloud {
       organization = "philbrook"
       workspaces {
         name    = "vault-onboarding-<example-name>"
         project = "AWS Vault LZs"
       }
     }
   }
   ```
3. Update the **Examples** table in this file with the new example directory and workspace name.
