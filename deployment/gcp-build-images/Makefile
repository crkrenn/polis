BASE_ENV ?= .env
PROD_ENV ?= prod.env
DEV_ENV ?= dev.env
DOCKER_ENV ?= docker_temp.env

export ENV_FILE = /dev/null

DOCKER_COMPOSE_FILE = ../../docker-compose.yml

# all:
# 	@echo "make PROD"
# 	@echo "make DEV"

# TTD: make PROD; make DEV
include ${BASE_ENV}
export $(shell sed 's/=.*//' ${BASE_ENV})

PROD: ## Run in prod mode (e.g. `make PROD start`, etc.)
	@echo Running in prod mode
	$(eval ENV_FILE = prod.env)
	$(eval include ${ENV_FILE})
	$(eval export $(shell sed 's/=.*//' ${ENV_FILE}))

DEV: ## Run in dev mode (e.g. `make DEV start`, etc.)
	@echo Running in dev mode
	$(eval ENV_FILE = dev.env)
	$(eval include ${ENV_FILE})
	$(eval export $(shell sed 's/=.*//' ${ENV_FILE}))

docker_env:
	$(shell cat ${BASE_ENV} > ${DOCKER_ENV})
	$(shell cat ${ENV_FILE} >> ${DOCKER_ENV})

set-project: docker_env ## set gcp project to value in DEV/PROD env
	@if [ -z ${GCP_PROJECT_ID} ]; then \
		echo "ERROR: GCP_PROJECT_ID not set"; \
		exit 1; \
	fi
	@if gcloud projects list | grep -e ${GCP_PROJECT_ID}; then \
		echo "setting google project to ${GCP_PROJECT_ID}"; \
		gcloud config set project ${GCP_PROJECT_ID}; \
	else \
		echo "ERROR: project ${GCP_PROJECT_ID} does not exist"; \
		exit 1; \
	fi

create-repos: docker_env set-project ## create gcp repos
	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
	export GCP_REGION=${GCP_REGION}; \
	export GCP_PROJECT_ID=${GCP_PROJECT_ID}; \
	export DOCKER_LOGIN=${DOCKER_LOGIN}; \
	export DOCKER_PASSWORD=${DOCKER_PASSWORD}; \
	../bin/create_repos.py

authorize-dockerhub: docker_env set-project ## make gcp repos
	@echo activating google cloud secrets manager (rerun if fails)
	@gcloud services enable secretmanager.googleapis.com
	@echo ${DOCKER_LOGIN} | gcloud secrets create docker-login --data-file=- \
            --replication-policy=user-managed \
            --locations=${GCP_REGION}
	@echo ${DOCKER_PASSWORD} | gcloud secrets create docker-password --data-file=- \
            --replication-policy=user-managed \
            --locations=${GCP_REGION}

echo_vars: docker_env
	@echo TAG=${TAG}

help:
	@echo 'Usage: make <command>'
	@echo
	@echo 'where <command> is one of the following:'
	@echo
	@grep -E '^[a-z0-9A-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help
