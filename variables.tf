variable "aws_auth" {
  description = "AWS auth backend role configuration. Set to null to skip creating the role."
  type = object({
    name                            = string
    backend                         = optional(string, "aws")
    bound_ami_ids                   = optional(list(string), [])
    bound_account_ids               = optional(list(string), [])
    bound_regions                   = optional(list(string), [])
    bound_vpc_ids                   = optional(list(string), [])
    bound_subnet_ids                = optional(list(string), [])
    bound_iam_role_arns             = optional(list(string), [])
    bound_iam_instance_profile_arns = optional(list(string), [])
    token_ttl                       = optional(number)
    token_max_ttl                   = optional(number)
    token_policies                  = optional(list(string), [])
  })
  default = null
}

variable "create_kv" {
  description = "Whether to create a KV policy for this role (requires aws_auth to be set)"
  type        = bool
  default     = false
}

variable "kv_mount_path" {
  description = "Path to the existing KV mount (required when create_kv is true)"
  type        = string
  default     = "kv"
}

variable "kv_path" {
  description = "Path within the KV mount to grant access to (required when create_kv is true)"
  type        = string
  default     = ""
}
