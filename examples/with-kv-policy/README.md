# Example with KV Policy

This example demonstrates how to use the Terraform Vault App Onboarding module to create an AWS auth role with an automatically generated KV policy.

## Usage

1. Configure your Vault provider in `versions.tf`
2. Ensure you have a KV secrets engine mounted at the path specified in `kv_mount_path` (default: "secret")
3. Run the following commands:

```bash
terraform init
terraform plan
terraform apply
```

## What This Creates

- An AWS auth role named "my-app-role" that allows authentication from:
  - AWS account ID: 123456789012
  - IAM role ARN: arn:aws:iam::123456789012:role/my-app-role
- A Vault policy named "my-app-role-kv-policy" that grants access to:
  - `secret/data/apps/my-app/*` (CRUD operations)
  - `secret/metadata/apps/my-app/*` (read, list, delete operations)
- The policy is automatically attached to the AWS auth role
- Token TTL: 1 hour (3600 seconds)
- Token max TTL: 2 hours (7200 seconds)

## KV Policy Details

The generated policy grants the following capabilities:

- **Data Path** (`secret/data/apps/my-app/*`): create, read, update, delete, list
- **Metadata Path** (`secret/metadata/apps/my-app/*`): read, list, delete

This allows the authenticated role to manage secrets under the specified path in the KV secrets engine.
