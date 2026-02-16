# Terraform Vault App Onboarding

A Terraform module for provisioning AWS auth roles in HashiCorp Vault with optional KV policy creation.

## Features

- Provisions AWS auth backend roles in Vault
- Dynamically looks up the AWS auth backend using a data source
- Optional KV policy creation for granting access to specific KV paths
- Supports all AWS auth role binding options (AMI, account, region, VPC, subnet, IAM role, etc.)

## Usage

### Basic Usage

```hcl
module "app_auth_role" {
  source = "github.com/nphilbrook/terraform-vault-app-onboarding"

  name               = "my-app-role"
  backend            = "aws"
  bound_account_id   = ["123456789012"]
  bound_iam_role_arn = ["arn:aws:iam::123456789012:role/my-app-role"]
}
```

### With KV Policy

```hcl
module "app_auth_role_with_kv" {
  source = "github.com/nphilbrook/terraform-vault-app-onboarding"

  name               = "my-app-role"
  backend            = "aws"
  bound_account_id   = ["123456789012"]
  bound_iam_role_arn = ["arn:aws:iam::123456789012:role/my-app-role"]
  
  create_kv       = true
  kv_mount_path   = "secret"
  kv_path         = "apps/my-app"
  
  token_policies = ["default"]
  token_ttl      = 3600
  token_max_ttl  = 7200
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.0 |
| vault | >= 3.0 |

## Providers

| Name | Version |
|------|---------|
| vault | >= 3.0 |

## Resources

| Name | Type |
|------|------|
| [vault_aws_auth_backend_role.this](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/aws_auth_backend_role) | resource |
| [vault_policy.kv](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/policy) | resource |
| [vault_auth_backend.aws](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/data-sources/auth_backend) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| name | Name of the AWS auth role | `string` | n/a | yes |
| backend | Path to the AWS auth backend | `string` | `"aws"` | no |
| create_kv | Whether to create a KV policy for this role | `bool` | `false` | no |
| kv_mount_path | Path to the existing KV mount (required when create_kv is true) | `string` | `""` | no |
| kv_path | Path within the KV mount to grant access to (required when create_kv is true) | `string` | `""` | no |
| bound_ami_id | List of AMI IDs that are allowed to authenticate | `list(string)` | `[]` | no |
| bound_account_id | List of AWS account IDs that are allowed to authenticate | `list(string)` | `[]` | no |
| bound_region | List of AWS regions that are allowed to authenticate | `list(string)` | `[]` | no |
| bound_vpc_id | List of VPC IDs that are allowed to authenticate | `list(string)` | `[]` | no |
| bound_subnet_id | List of subnet IDs that are allowed to authenticate | `list(string)` | `[]` | no |
| bound_iam_role_arn | List of IAM role ARNs that are allowed to authenticate | `list(string)` | `[]` | no |
| bound_iam_instance_profile_arn | List of IAM instance profile ARNs that are allowed to authenticate | `list(string)` | `[]` | no |
| token_ttl | The TTL period of tokens issued using this role in seconds | `number` | `null` | no |
| token_max_ttl | The maximum lifetime of tokens issued using this role in seconds | `number` | `null` | no |
| token_policies | List of policies to attach to tokens issued using this role | `list(string)` | `[]` | no |

## Outputs

| Name | Description |
|------|-------------|
| role_name | Name of the created AWS auth role |
| backend_path | Path to the AWS auth backend |
| policy_name | Name of the KV policy (if created) |
| role_id | The ID of the AWS auth role |

## License

Apache 2.0 License