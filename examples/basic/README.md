# Basic Example

This example demonstrates the basic usage of the Terraform Vault App Onboarding module to create an AWS auth role in Vault.

## Usage

1. Configure your Vault provider in `versions.tf`
2. Run the following commands:

```bash
terraform init
terraform plan
terraform apply
```

## What This Creates

- An AWS auth role named "my-app-role" that allows authentication from:
  - AWS account ID: 123456789012
  - IAM role ARN: arn:aws:iam::123456789012:role/my-app-role
- Token TTL: 1 hour (3600 seconds)
- Token max TTL: 2 hours (7200 seconds)
