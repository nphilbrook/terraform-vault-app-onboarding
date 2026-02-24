terraform {
  cloud {
    organization = "philbrook"
    workspaces {
      name    = "vault-onboarding-with-kv-policy"
      project = "AWS Vault LZs"
    }
  }
}
