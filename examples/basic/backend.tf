terraform {
  cloud {
    organization = "philbrook"
    workspaces {
      name    = "vault-onboarding-basic"
      project = "AWS Vault LZs"
    }
  }
}
