# create google secrets

# @TODO: add a variable for the secret name; use list iteration to create multiple secrets

variable "GCP_REGION" {type = string}
variable "GCP_PROJECT_ID" {type = string}
variable "GCP_PROJECT_NUMBER" {type = string}
variable "DOCKER_REPO" {type = string}
variable "DOCKER_LOGIN" {type = string}
variable "DOCKER_PASSWORD" {type = string}
variable "GCP_AUTH_FILE" {
  type = string
  default = "~/.config/gcloud/application_default_credentials.json"
}

terraform {
  required_version = ">= 0.12"
}
provider "google" {
  project     = var.GCP_PROJECT_ID
  credentials = file(var.GCP_AUTH_FILE)
  region      = var.GCP_REGION
}

resource "google_project_service" "secretmanager" {
  project = var.GCP_PROJECT_ID
  service = "secretmanager.googleapis.com"

  timeouts {
    create = "30m"
    update = "40m"
  }

  disable_dependent_services = true
}

# Create a secret for docker-login
resource "google_secret_manager_secret" "docker-login" {
  secret_id   = "docker-login"
  replication {
    user_managed {
      replicas {
        location = var.GCP_REGION
      }
    }
  }
  depends_on = [
    google_project_service.secretmanager
  ]
}
# Add the secret data for local-docker-login secret
resource "google_secret_manager_secret_version" "docker-login" {
  secret = google_secret_manager_secret.docker-login.id
  secret_data = var.DOCKER_LOGIN
}

# Create a secret for docker-password
resource "google_secret_manager_secret" "docker-password" {
  secret_id   = "docker-password"
  replication {
    user_managed {
      replicas {
        location = var.GCP_REGION
      }
    }
  }
  depends_on = [
    google_project_service.secretmanager
  ]
}
# Add the secret data for local-docker-password secret
resource "google_secret_manager_secret_version" "docker-password" {
  secret = google_secret_manager_secret.docker-password.id
  secret_data = var.DOCKER_PASSWORD
}

# Create a secret for docker-repo
resource "google_secret_manager_secret" "docker-repo" {
  secret_id   = "docker-repo"
  replication {
    user_managed {
      replicas {
        location = var.GCP_REGION
      }
    }
  }
  depends_on = [
    google_project_service.secretmanager
  ]
}
# Add the secret data for local-docker-repo secret
resource "google_secret_manager_secret_version" "docker-repo" {
  secret = google_secret_manager_secret.docker-repo.id
  secret_data = "${var.DOCKER_REPO}"
}

resource "google_secret_manager_secret_iam_member" "docker-repo" {
  project = google_secret_manager_secret.docker-repo.project
  secret_id = google_secret_manager_secret.docker-repo.secret_id
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${var.GCP_PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "docker-login" {
  project = google_secret_manager_secret.docker-login.project
  secret_id = google_secret_manager_secret.docker-login.secret_id
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${var.GCP_PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "docker-password" {
  project = google_secret_manager_secret.docker-password.project
  secret_id = google_secret_manager_secret.docker-password.secret_id
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${var.GCP_PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
}

# resource "google_secret_manager_secret_iam_binding" "docker-repo" {
#   project = google_secret_manager_secret.docker-repo.project
#   secret_id = google_secret_manager_secret.docker-repo.secret_id
#   role = "roles/secretmanager.secretAccessor"
#   members = [
#       "user:${var.GCP_PROJECT_NUMBER}@cloudbuild.gserviceaccount.com",
#   ]
# }

# data "google_iam_policy" "admin" {
#   binding {
#     role = "roles/secretmanager.secretAccessor"
#     members = [
#       "user:${GCP_PROJECT_NUMBER}@cloudbuild.gserviceaccount.com",
#     ]
#   }
# }

# resource "google_secret_manager_secret_iam_policy" "docker-login" {
#   project = google_secret_manager_secret.docker-login.project
#   secret_id = google_secret_manager_secret.docker-login.secret_id
#   policy_data = data.google_iam_policy.admin.policy_data
# }

# resource "google_secret_manager_secret_iam_policy" "docker-password" {
#   project = google_secret_manager_secret.docker-password.project
#   secret_id = google_secret_manager_secret.docker-password.secret_id
#   policy_data = data.google_iam_policy.admin.policy_data
# }
# resource "google_secret_manager_secret_iam_policy" "docker-repo" {
#   project = google_secret_manager_secret.docker-repo.project
#   secret_id = google_secret_manager_secret.docker-repo.secret_id
#   policy_data = data.google_iam_policy.admin.policy_data
# }