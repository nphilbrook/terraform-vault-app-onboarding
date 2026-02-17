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

  name                 = "my-app-role"
  backend              = "aws"
  bound_account_ids    = ["123456789012"]
  bound_iam_role_arns  = ["arn:aws:iam::123456789012:role/my-app-role"]
}
```

### With KV Policy

```hcl
module "app_auth_role_with_kv" {
  source = "github.com/nphilbrook/terraform-vault-app-onboarding"

  name                 = "my-app-role"
  backend              = "aws"
  bound_account_ids    = ["123456789012"]
  bound_iam_role_arns  = ["arn:aws:iam::123456789012:role/my-app-role"]
  
  create_kv       = true
  kv_mount_path   = "secret"
  kv_path         = "apps/my-app"
  
  token_policies = ["default"]
  token_ttl      = 3600
  token_max_ttl  = 7200
}
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.14 |
| <a name="requirement_vault"></a> [vault](#requirement\_vault) | ~> 5.7 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_vault"></a> [vault](#provider\_vault) | ~> 5.7 |

## Resources

| Name | Type |
|------|------|
| [vault_aws_auth_backend_role.this](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/aws_auth_backend_role) | resource |
| [vault_policy.kv](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/policy) | resource |
| [vault_auth_backend.aws](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/data-sources/auth_backend) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_name"></a> [name](#input\_name) | Name of the AWS auth role | `string` | n/a | yes |
| <a name="input_backend"></a> [backend](#input\_backend) | Path to the AWS auth backend | `string` | `"aws"` | no |
| <a name="input_bound_account_ids"></a> [bound\_account\_ids](#input\_bound\_account\_ids) | List of AWS account IDs that are allowed to authenticate | `list(string)` | `[]` | no |
| <a name="input_bound_ami_ids"></a> [bound\_ami\_ids](#input\_bound\_ami\_ids) | List of AMI IDs that are allowed to authenticate | `list(string)` | `[]` | no |
| <a name="input_bound_iam_instance_profile_arns"></a> [bound\_iam\_instance\_profile\_arns](#input\_bound\_iam\_instance\_profile\_arns) | List of IAM instance profile ARNs that are allowed to authenticate | `list(string)` | `[]` | no |
| <a name="input_bound_iam_role_arns"></a> [bound\_iam\_role\_arns](#input\_bound\_iam\_role\_arns) | List of IAM role ARNs that are allowed to authenticate | `list(string)` | `[]` | no |
| <a name="input_bound_regions"></a> [bound\_regions](#input\_bound\_regions) | List of AWS regions that are allowed to authenticate | `list(string)` | `[]` | no |
| <a name="input_bound_subnet_ids"></a> [bound\_subnet\_ids](#input\_bound\_subnet\_ids) | List of subnet IDs that are allowed to authenticate | `list(string)` | `[]` | no |
| <a name="input_bound_vpc_ids"></a> [bound\_vpc\_ids](#input\_bound\_vpc\_ids) | List of VPC IDs that are allowed to authenticate | `list(string)` | `[]` | no |
| <a name="input_create_kv"></a> [create\_kv](#input\_create\_kv) | Whether to create a KV policy for this role | `bool` | `false` | no |
| <a name="input_kv_mount_path"></a> [kv\_mount\_path](#input\_kv\_mount\_path) | Path to the existing KV mount (required when create\_kv is true) | `string` | `"kv"` | no |
| <a name="input_kv_path"></a> [kv\_path](#input\_kv\_path) | Path within the KV mount to grant access to (required when create\_kv is true) | `string` | `""` | no |
| <a name="input_token_max_ttl"></a> [token\_max\_ttl](#input\_token\_max\_ttl) | The maximum lifetime of tokens issued using this role in seconds | `number` | `null` | no |
| <a name="input_token_policies"></a> [token\_policies](#input\_token\_policies) | List of policies to attach to tokens issued using this role | `list(string)` | `[]` | no |
| <a name="input_token_ttl"></a> [token\_ttl](#input\_token\_ttl) | The TTL period of tokens issued using this role in seconds | `number` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_backend_path"></a> [backend\_path](#output\_backend\_path) | Path to the AWS auth backend |
| <a name="output_policy_name"></a> [policy\_name](#output\_policy\_name) | Name of the KV policy (if created) |
| <a name="output_role_id"></a> [role\_id](#output\_role\_id) | The ID of the AWS auth role |
| <a name="output_role_name"></a> [role\_name](#output\_role\_name) | Name of the created AWS auth role |
<!-- END_TF_DOCS -->