output "role_name" {
  description = "Name of the created AWS auth role"
  value       = vault_aws_auth_backend_role.this.role
}

output "backend_path" {
  description = "Path to the AWS auth backend"
  value       = vault_aws_auth_backend_role.this.backend
}

output "policy_name" {
  description = "Name of the KV policy (if created)"
  value       = var.create_kv ? vault_policy.kv[0].name : null
}

output "role_id" {
  description = "The ID of the AWS auth role"
  value       = vault_aws_auth_backend_role.this.role_id
}
