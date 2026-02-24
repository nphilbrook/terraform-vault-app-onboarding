output "role_name" {
  description = "Name of the created AWS auth role"
  value       = var.aws_auth != null ? vault_aws_auth_backend_role.this[0].role : null
}

output "backend_path" {
  description = "Path to the AWS auth backend"
  value       = var.aws_auth != null ? vault_aws_auth_backend_role.this[0].backend : null
}

output "policy_name" {
  description = "Name of the KV policy (if created)"
  value       = var.aws_auth != null && var.create_kv ? vault_policy.kv[0].name : null
}

output "role_id" {
  description = "The ID of the AWS auth role"
  value       = var.aws_auth != null ? vault_aws_auth_backend_role.this[0].role_id : null
}
