locals {
  create_role = var.aws_auth != null
  create_kv   = var.create_kv
}

moved {
  from = vault_aws_auth_backend_role.this
  to   = vault_aws_auth_backend_role.this[0]
}

# Lookup the AWS auth backend
data "vault_auth_backend" "aws" {
  count = local.create_role ? 1 : 0
  path  = var.aws_auth.backend
}

# Create the AWS auth role
resource "vault_aws_auth_backend_role" "this" {
  count = local.create_role ? 1 : 0

  backend = data.vault_auth_backend.aws[0].path
  role    = "applz-${var.app_name}"

  auth_type            = "iam"
  inferred_entity_type = "ec2_instance"
  # TODO: look up with data source
  # TODO: What happens with replication and this value?!
  inferred_aws_region = "us-west-2"

  bound_ami_ids                   = var.aws_auth.bound_ami_ids
  bound_account_ids               = var.aws_auth.bound_account_ids
  bound_regions                   = var.aws_auth.bound_regions
  bound_vpc_ids                   = var.aws_auth.bound_vpc_ids
  bound_subnet_ids                = var.aws_auth.bound_subnet_ids
  bound_iam_role_arns             = var.aws_auth.bound_iam_role_arns
  bound_iam_instance_profile_arns = var.aws_auth.bound_iam_instance_profile_arns

  token_ttl     = var.aws_auth.token_ttl
  token_max_ttl = var.aws_auth.token_max_ttl

  # Combine both the user-provided policies and the KV policy (if created)
  token_policies = concat(
    var.aws_auth.token_policies,
    var.create_kv ? [vault_policy.kv[0].name] : []
  )
}

# Create a policy granting access to the KV path if create_kv is true
resource "vault_policy" "kv" {
  count = local.create_kv ? 1 : 0

  name = "applz-kv-${var.app_name}"

  policy = <<EOT
# Allow access to the KV path
path "${var.kv_mount_path}/data/${var.app_name}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "${var.kv_mount_path}/metadata/${var.app_name}/*" {
  capabilities = ["read", "list", "delete"]
}
EOT

  lifecycle {
    precondition {
      condition     = var.kv_mount_path != ""
      error_message = "kv_mount_path must be specified when create_kv is true."
    }
  }
}
