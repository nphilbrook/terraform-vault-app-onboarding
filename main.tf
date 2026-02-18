# Lookup the AWS auth backend
data "vault_auth_backend" "aws" {
  path = var.backend
}

# Create the AWS auth role
resource "vault_aws_auth_backend_role" "this" {
  backend = data.vault_auth_backend.aws.path
  role    = "applz-${var.name}"

  auth_type            = "iam"
  inferred_entity_type = "ec2_instance"
  # TODO: look up with data source
  # TODO: What happens with replication and this value?!
  inferred_aws_region = "us-west-2"

  bound_ami_ids                   = var.bound_ami_ids
  bound_account_ids               = var.bound_account_ids
  bound_regions                   = var.bound_regions
  bound_vpc_ids                   = var.bound_vpc_ids
  bound_subnet_ids                = var.bound_subnet_ids
  bound_iam_role_arns             = var.bound_iam_role_arns
  bound_iam_instance_profile_arns = var.bound_iam_instance_profile_arns

  token_ttl     = var.token_ttl
  token_max_ttl = var.token_max_ttl

  # Combine both the user-provided policies and the KV policy (if created)
  token_policies = concat(
    var.token_policies,
    var.create_kv ? [vault_policy.kv[0].name] : []
  )
}

# Create a policy granting access to the KV path if create_kv is true
resource "vault_policy" "kv" {
  count = var.create_kv ? 1 : 0

  name = "applz-${var.name}-kv-policy"

  policy = <<EOT
# Allow access to the KV path
path "${var.kv_mount_path}/data/${var.kv_path}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "${var.kv_mount_path}/metadata/${var.kv_path}/*" {
  capabilities = ["read", "list", "delete"]
}
EOT

  lifecycle {
    precondition {
      condition     = var.kv_mount_path != ""
      error_message = "kv_mount_path must be specified when create_kv is true."
    }

    precondition {
      condition     = var.kv_path != ""
      error_message = "kv_path must be specified when create_kv is true."
    }
  }
}
