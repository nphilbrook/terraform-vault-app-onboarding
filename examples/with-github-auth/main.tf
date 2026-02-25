module "app_github_auth" {
  source = "../.."

  app_name = "my-app"

  github_auth = {
    backend             = "jwt"
    github_organization = "my-org"
    github_repositories = ["my-app-repo", "my-app-infra"]
    token_ttl           = 300
  }

  # Enable KV policy creation
  create_kv_policy = true
  kv_mount_path    = "secret"
}

output "github_role_name" {
  value = module.app_github_auth.github_role_name
}

output "policy_name" {
  value = module.app_github_auth.policy_name
}
