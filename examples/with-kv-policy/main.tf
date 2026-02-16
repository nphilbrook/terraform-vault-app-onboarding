module "app_auth_role_with_kv" {
  source = "../.."

  name               = "my-app-role"
  backend            = "aws"
  bound_account_id   = ["123456789012"]
  bound_iam_role_arn = ["arn:aws:iam::123456789012:role/my-app-role"]
  
  # Enable KV policy creation
  create_kv       = true
  kv_mount_path   = "secret"
  kv_path         = "apps/my-app"
  
  token_policies = ["default"]
  token_ttl      = 3600
  token_max_ttl  = 7200
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
