terraform {
  required_version = ">= 1.0"

  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = ">= 3.0"
    }
  }
}

provider "vault" {
  # Configure the Vault provider
  # address = "http://localhost:8200"
  # token   = "your-vault-token"
}
