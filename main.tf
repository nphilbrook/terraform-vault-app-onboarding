# Lookup the AWS auth backend
data "vault_auth_backend" "aws" {
  path = var.backend
}

# Create the AWS auth role
resource "vault_aws_auth_backend_role" "this" {
  backend = data.vault_auth_backend.aws.path
  role    = var.name

  auth_type = "iam"

  bound_ami_ids                   = var.bound_ami_id
  bound_account_ids               = var.bound_account_id
  bound_regions                   = var.bound_region
  bound_vpc_ids                   = var.bound_vpc_id
  bound_subnet_ids                = var.bound_subnet_id
  bound_iam_role_arns             = var.bound_iam_role_arn
  bound_iam_instance_profile_arns = var.bound_iam_instance_profile_arn

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

  name = "${var.name}-kv-policy"

  policy = <<EOT
# Allow access to the KV path
path "${var.kv_mount_path}/data/${var.kv_path}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "${var.kv_mount_path}/metadata/${var.kv_path}/*" {
  capabilities = ["read", "list", "delete"]
}
EOT
}
