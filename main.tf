locals {
  create_role        = var.aws_auth != null
  create_github_role = var.github_auth != null
  create_kv          = var.create_kv_policy
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
    var.create_kv_policy ? [vault_policy.kv[0].name] : []
  )
}

# Lookup the jwt-github auth backend
data "vault_auth_backend" "github" {
  count = local.create_github_role ? 1 : 0
  path  = var.github_auth.backend
}

# Create the GitHub Actions JWT auth backend role
resource "vault_jwt_auth_backend_role" "github" {
  count = local.create_github_role ? 1 : 0

  # namespace = var.github_auth.vault_namespace_path
  backend = data.vault_auth_backend.github[0].path

  role_name         = "applz-${var.app_name}-gha"
  bound_audiences   = coalesce(var.github_auth.bound_audiences, ["https://github.com/${var.github_auth.github_organization}"])
  bound_claims_type = "glob"
  bound_claims = {
    sub                = join(",", [for repo in var.github_auth.github_repositories : "repo:${var.github_auth.github_organization}/${repo}:ref:*"])
    workflow           = var.github_auth.workflow
    runner_environment = "self-hosted"
  }
  user_claim = "repository"
  role_type  = "jwt"
  token_ttl  = var.github_auth.token_ttl
  token_type = "service"

  token_policies = concat(
    var.github_auth.token_policies,
    var.create_kv_policy ? [vault_policy.kv[0].name] : []
  )
}
