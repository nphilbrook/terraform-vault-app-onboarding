module "app_auth_role" {
  source = "../.."

  name                = "my-app-role"
  backend             = "aws"
  bound_account_ids   = ["123456789012"]
  bound_iam_role_arns = ["arn:aws:iam::123456789012:role/my-app-role"]

  token_ttl     = 3600
  token_max_ttl = 7200
}

output "role_name" {
  value = module.app_auth_role.role_name
}

output "role_id" {
  value = module.app_auth_role.role_id
}
