variable "name" {
  description = "Name of the AWS auth role"
  type        = string
}

variable "backend" {
  description = "Path to the AWS auth backend"
  type        = string
  default     = "aws"
}

variable "create_kv" {
  description = "Whether to create a KV policy for this role"
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

variable "bound_ami_ids" {
  description = "List of AMI IDs that are allowed to authenticate"
  type        = list(string)
  default     = []
}

variable "bound_account_ids" {
  description = "List of AWS account IDs that are allowed to authenticate"
  type        = list(string)
  default     = []
}

variable "bound_regions" {
  description = "List of AWS regions that are allowed to authenticate"
  type        = list(string)
  default     = []
}

variable "bound_vpc_ids" {
  description = "List of VPC IDs that are allowed to authenticate"
  type        = list(string)
  default     = []
}

variable "bound_subnet_ids" {
  description = "List of subnet IDs that are allowed to authenticate"
  type        = list(string)
  default     = []
}

variable "bound_iam_role_arns" {
  description = "List of IAM role ARNs that are allowed to authenticate"
  type        = list(string)
  default     = []
}

variable "bound_iam_instance_profile_arns" {
  description = "List of IAM instance profile ARNs that are allowed to authenticate"
  type        = list(string)
  default     = []
}

variable "token_ttl" {
  description = "The TTL period of tokens issued using this role in seconds"
  type        = number
  default     = null
}

variable "token_max_ttl" {
  description = "The maximum lifetime of tokens issued using this role in seconds"
  type        = number
  default     = null
}

variable "token_policies" {
  description = "List of policies to attach to tokens issued using this role"
  type        = list(string)
  default     = []
}
