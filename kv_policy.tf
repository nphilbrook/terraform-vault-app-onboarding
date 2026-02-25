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
