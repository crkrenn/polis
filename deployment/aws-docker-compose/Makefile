BASE_ENV ?= .env
PROD_ENV ?= prod.env
DEV_ENV ?= dev.env
DOCKER_ENV ?= docker_temp.env
DOCKER_COMPOSE_FILE ?= docker-compose.yml

export ENV_FILE = /dev/null
export GIT_HASH = $(shell git rev-parse --short HEAD)

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

export DOCKER_DETACHED=--detach

ATTACHED: ## Run docker in "attached" mode, with output from all containers streaming to the terminal
	$(eval undefine DOCKER_DETACHED)

docker_env:
	$(shell cat ${BASE_ENV} > ${DOCKER_ENV})
	$(shell cat ${ENV_FILE} >> ${DOCKER_ENV})

clean: ## reset push-images, so they will be rerun
	@rm -f push-images

verify-project:
	@if [ -z ${GCP_PROJECT_ID} ]; then \
		echo "ERROR: GCP_PROJECT_ID not set"; \
		exit 1; \
	fi
	@if ! gcloud projects list | grep -e ${GCP_PROJECT_ID}; then \
		echo "ERROR: project ${GCP_PROJECT_ID} does not exist"; \
		exit 1; \
	fi

push-images: ## push images to AWS ECR
	@make verify-project
	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
	export TAG=${TAG}; \
	export IMAGE_REPO=${IMAGE_REPO}; \
	export AWS_REGION=${AWS_REGION}; \
	../bin/push_images.py
	touch push-images

start-local: docker_env echo_vars ## Start all Docker containers on local machine
	docker-compose --env-file ${DOCKER_ENV} up ${DOCKER_DETACHED}

stop-local: docker_env echo_vars ## Start all Docker containers on local machine
	docker-compose --env-file ${DOCKER_ENV} down ${DOCKER_DETACHED}

stop-ALL:  ## Stop all running containers
	@-docker container stop $(shell docker container ls -q)

build-docker-compose: ## build docker-compose
	@make verify-project
	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
	export GCP_REGION=${GCP_REGION}; \
	export GCP_PROJECT_ID=${GCP_PROJECT_ID}; \
	export IMAGE_REPO=${IMAGE_REPO}; \
	export TAG=${TAG}; \
	../bin/build_docker_compose.py




# set-project:  ## set google cloud project to value in DEV/PROD env
# 	make verify-project
# 	echo "setting google project to ${GCP_PROJECT_ID}"
# 	gcloud config set project ${GCP_PROJECT_ID}
# 	touch set-project

# # create-repos: ## create google cloud repos
# # 	make verify-project
# # 	make set-project
# # 	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
# # 	export GCP_REGION=${GCP_REGION}; \
# # 	export GCP_PROJECT_ID=${GCP_PROJECT_ID}; \
# # 	export DOCKER_REPO=${DOCKER_REPO}; \
# # 	export DOCKER_LOGIN=${DOCKER_LOGIN}; \
# # 	export DOCKER_PASSWORD=${DOCKER_PASSWORD}; \
# # 	../bin/create_repos.py
# # 	touch create-repos

# authorize-dockerhub: ## connect google cloud to dockerhub
# 	make verify-project
# 	make set-project
# 	@echo "attempting to connect google cloud to dockerhub";
# 	@echo "deleting old secrets (if they exist)";
# 	-gcloud secrets delete docker-repo --quiet
# 	-gcloud secrets delete docker-login --quiet
# 	-gcloud secrets delete docker-password --quiet
# 	@echo "using terraform to create new secrets";
# 	@cd ../terraform/gcp_secrets; \
# 	terraform init; \
# 	export TF_VAR_GCP_REGION=${GCP_REGION} ; \
# 	export TF_VAR_GCP_PROJECT_ID=${GCP_PROJECT_ID} ; \
# 	export TF_VAR_GCP_PROJECT_NUMBER=${GCP_PROJECT_NUMBER} ; \
# 	export TF_VAR_DOCKER_REPO=${DOCKER_REPO} ; \
# 	export TF_VAR_DOCKER_LOGIN=${DOCKER_LOGIN} ; \
# 	export TF_VAR_DOCKER_PASSWORD=${DOCKER_PASSWORD} ; \
# 	terraform apply -auto-approve
# 	touch authorize-dockerhub

# build-images: ## build polis images and push to google cloud repos (~60 min)
# 	make verify-project
# 	make set-project
# 	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
# 	export TAG=${TAG}; \
# 	export GCP_REGION=${GCP_REGION}; \
# 	export GCP_PROJECT_ID=${GCP_PROJECT_ID}; \
# 	export GCP_PROJECT_NUMBER=${GCP_PROJECT_NUMBER}; \
# 	export DOCKER_REPO=${DOCKER_REPO}; \
# 	export DOCKER_LOGIN=${DOCKER_LOGIN}; \
# 	export DOCKER_PASSWORD=${DOCKER_PASSWORD}; \
# 	../bin/build_images.py
# 	cd ../.. ; \
# 	gcloud builds submit \
# 		--region=${GCP_REGION} \
# 		--config=deployment/gcp-build-images/cloudbuild.yaml

# # @echo "activating google cloud secrets manager (rerun if fails)"
# # @gcloud services enable secretmanager.googleapis.com
# # @echo ${DOCKER_LOGIN} | gcloud secrets update docker-login --data-file=- \
# # 		--replication-policy=user-managed \
# # 		--locations=${GCP_REGION}
# # @echo ${DOCKER_PASSWORD} | gcloud secrets create docker-password --data-file=- \
# # 		--replication-policy=user-managed \
# # 		--locations=${GCP_REGION}

# # add-ssl-cert-tf: ## create and validate ssl certificate with terraform
# # 	-@echo "attempting to create aws load balancer"; \
# # 	cd terraform_ssl; \
# # 	terraform init; \
# # 	export TF_VAR_DEBUG=${DEBUG}; \
# # 	export TF_VAR_service_name=${SERVICE_NAME}; \
# # 	export TF_VAR_hosted_zone=${AWS_HOSTED_ZONE}; \
# # 	export TF_VAR_hosted_zone_id=${AWS_HOSTED_ZONE_ID}; \

# # 	terraform plan

# # gcloud secrets create SECRET [--data-file=PATH] [--labels=[KEY=VALUE,...]]
# #     [--set-annotations=[KEY=VALUE,...]] [--topics=[TOPICS,...]]
# #     [--expire-time=EXPIRE-TIME | --ttl=TTL]
# #     [--next-rotation-time=NEXT_ROTATION_TIME
# #       --rotation-period=ROTATION_PERIOD]
# #     [--replication-policy-file=REPLICATION-POLICY-FILE
# #       | --kms-key-name=KMS-KEY-NAME
# #       --locations=[LOCATION,...] --replication-policy=POLICY]
# #     [GCLOUD_WIDE_FLAG ...]

# # gcloud secrets update SECRET [--etag=ETAG]
# # [--update-labels=[KEY=VALUE,...]]
# # [--add-topics=[ADD-TOPICS,...] | --clear-topics
# #   | --remove-topics=[REMOVE-TOPICS,...]]
# # [--clear-annotations | --remove-annotations=[KEY,...]
# #   | --update-annotations=[KEY=VALUE,...]]
# # [--clear-labels | --remove-labels=[KEY,...]]
# # [--clear-version-aliases | --remove-version-aliases=[KEY,...]
# #   | --update-version-aliases=[KEY=VALUE,...]]
# # [--expire-time=EXPIRE-TIME | --remove-expiration | --ttl=TTL]
# # [--next-rotation-time=NEXT_ROTATION_TIME --remove-next-rotation-time
# #   --remove-rotation-period
# #   --remove-rotation-schedule --rotation-period=ROTATION_PERIOD]
# # [GCLOUD_WIDE_FLAG ...]

echo_vars: docker_env
	@echo TAG=${TAG}

help:
	@echo 'Usage: make <command>'
	@echo
	@echo 'where <command> is one of the following:'
	@echo
	@grep -E '^[a-z0-9A-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo 'Note: set-project, create-repos, & authorize-dockerhub are "sticky" commands.'
	@echo '      They will be run once, and then not run again unless you run "make clean" first.'
	@echo 'Note: some targets (e.g. ATTACHED) require GNU Make version 3.82 or above.'
.DEFAULT_GOAL := help
