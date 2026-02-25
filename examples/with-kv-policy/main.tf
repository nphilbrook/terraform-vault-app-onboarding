module "app_auth_role_with_kv" {
  source = "../.."

  app_name = "my-app"

  aws_auth = {
    backend             = "aws"
    bound_account_ids   = ["123456789012"]
    bound_iam_role_arns = ["arn:aws:iam::123456789012:role/my-app-role"]
    token_policies      = ["default"]
    token_ttl           = 3600
    token_max_ttl       = 7200
  }

  # Enable KV policy creation
  create_kv_policy = true
  kv_mount_path    = "secret"
}

output "role_name" {
  value = module.app_auth_role_with_kv.role_name
}

output "role_id" {
  value = module.app_auth_role_with_kv.role_id
}

output "policy_name" {
  value = module.app_auth_role_with_kv.policy_name
}
