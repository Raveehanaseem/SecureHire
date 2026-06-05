# SecureHire — Infrastructure as Code
# CYC386 Requirement: Terraform + HashiCorp Vault
# Provider: Docker (local dev) — swap for AWS/GCP for cloud

terraform {
  required_version = ">= 1.7"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    vault = {
      source  = "hashicorp/vault"
      version = "~> 4.0"
    }
  }
}

# ── Providers ─────────────────────────────────────────────────────────────────
provider "docker" {}

provider "vault" {
  address = var.vault_addr
  token   = var.vault_token
}

# ── Variables ─────────────────────────────────────────────────────────────────
variable "vault_addr" {
  default = "http://localhost:8200"
}
variable "vault_token" {
  default     = ""
  sensitive   = true
}
variable "db_password" {
  default     = "securehire123"
  sensitive   = true
}
variable "jwt_secret" {
  default     = "CYC386-jwt-secret-key-very-long-and-secure-2026!!"
  sensitive   = true
}
variable "aes_key" {
  default     = "CYC386-aes-256-key-securehire-2026"
  sensitive   = true
}

# ── Vault: Store secrets ───────────────────────────────────────────────────────
resource "vault_kv_secret_v2" "securehire_app" {
  mount = "secret"
  name  = "securehire/app"

  data_json = jsonencode({
    jwt_secret_key = var.jwt_secret
    aes_key        = var.aes_key
    db_password    = var.db_password
  })
}

resource "vault_kv_secret_v2" "securehire_db" {
  mount = "secret"
  name  = "securehire/database"

  data_json = jsonencode({
    username = "securehire"
    password = var.db_password
    host     = "postgres"
    port     = "5432"
    dbname   = "securehire_db"
  })
}

# ── Docker Network ─────────────────────────────────────────────────────────────
resource "docker_network" "securehire_net" {
  name   = "securehire_net"
  driver = "bridge"
}

# ── PostgreSQL Container ───────────────────────────────────────────────────────
resource "docker_container" "postgres" {
  name  = "securehire_postgres_tf"
  image = "postgres:16-alpine"

  env = [
    "POSTGRES_DB=securehire_db",
    "POSTGRES_USER=securehire",
    "POSTGRES_PASSWORD=${var.db_password}",
  ]

  ports {
    internal = 5432
    external = 5432
  }

  networks_advanced {
    name = docker_network.securehire_net.name
  }

  volumes {
    volume_name    = "postgres_data_tf"
    container_path = "/var/lib/postgresql/data"
  }

  restart = "unless-stopped"
}

# ── Redis Container ────────────────────────────────────────────────────────────
resource "docker_container" "redis" {
  name  = "securehire_redis_tf"
  image = "redis:7-alpine"

  ports {
    internal = 6379
    external = 6379
  }

  networks_advanced {
    name = docker_network.securehire_net.name
  }

  restart = "unless-stopped"
}

# ── Outputs ────────────────────────────────────────────────────────────────────
output "postgres_host" {
  value = "localhost:5432"
}
output "redis_host" {
  value = "localhost:6379"
}
output "vault_secret_path" {
  value = vault_kv_secret_v2.securehire_app.path
}
