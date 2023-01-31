BASE_ENV ?= .env
PROD_ENV ?= prod.env
DEV_ENV ?= dev.env
DOCKER_ENV ?= docker_temp.env

export ENV_FILE = /dev/null

DOCKER_COMPOSE_FILE = ../../docker-compose.yml

include ${BASE_ENV}
export $(shell sed 's/=.*//' ${BASE_ENV})

update_polis_config: ## Copy polis.config.js to client-* directories
	@echo "Copying polis.config.js (if present) to client-* directories"
	@echo "Renaming polis.config.template.js to polis.config.template.js.bak"
	@-cp ../../polis.config.js ../../client-participation
	@-cp ../../polis.config.js ../../client-admin
	@-cp ../../polis.config.js ../../client-report
	@-mv ../../client-participation/polis.config.template.js \
		../../client-participation/polis.config.template.js.bak
	@-mv ../../client-admin/polis.config.template.js \
		../../client-admin/polis.config.template.js.bak
	@-mv ../../client-report/polis.config.template.js \
		../../client-report/polis.config.template.js.bak
	@-sed -i "" -e "s/COPY polis.config.template.js/#COPY polis.config.template.js/" \
		../../client-*/Dockerfile

revert_polis_config: ## Revert polis.config.js in client-* directories
	@echo "Deleting polis.config.js (if present) in client-* directories"
	@-rm ../../client-*/polis.config.js
	@-mv ../../client-participation/polis.config.template.js.bak \
		../../client-participation/polis.config.template.js
	@-mv ../../client-admin/polis.config.template.js.bak \
		../../client-admin/polis.config.template.js
	@-mv ../../client-report/polis.config.template.js.bak \
		../../client-report/polis.config.template.js
	@-sed -i "" -e "s/#COPY polis.config.template.js/COPY polis.config.template.js/" \
		../../client-*/Dockerfile

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

# clean: ## reset create-repos and authorize-dockerhub, so they will be rerun
# 	@rm -f create-repos authorize-dockerhub

docker_env:
	$(shell cat ${BASE_ENV} > ${DOCKER_ENV})
	$(shell cat ${ENV_FILE} >> ${DOCKER_ENV})

verify-project:
	@if [ -z ${GCP_PROJECT_ID} ]; then \
		echo "ERROR: GCP_PROJECT_ID not set"; \
		exit 1; \
	fi
	@if ! gcloud projects list | grep -e ${GCP_PROJECT_ID}; then \
		echo "ERROR: project ${GCP_PROJECT_ID} does not exist"; \
		exit 1; \
	fi

set-project:  ## set google cloud project to value in DEV/PROD env
	make verify-project
	echo "setting google project to ${GCP_PROJECT_ID}"
	gcloud config set project ${GCP_PROJECT_ID}

build-images: ## build polis images and push to google cloud repos (~60 min)
	make verify-project
	make set-project
	make update_polis_config
	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
	export TAG=${TAG}; \
	export GCP_REGION=${GCP_REGION}; \
	export GCP_PROJECT_ID=${GCP_PROJECT_ID}; \
	export GCP_PROJECT_NUMBER=${GCP_PROJECT_NUMBER}; \
	export DOCKER_REPO=${DOCKER_REPO}; \
	export DOCKER_LOGIN=${DOCKER_LOGIN}; \
	export DOCKER_PASSWORD=${DOCKER_PASSWORD}; \
	../bin/build_images.py
	cd ../.. ; \
	gcloud builds submit \
		--region=${GCP_REGION} \
		--config=deployment/gcp-build-images/cloudbuild.yaml 2>&1 | \
	ts -s "%.s || %H:%M:%S ||"
	make revert_polis_config


echo_vars: docker_env
	@echo TAG=${TAG}

help:
	@echo 'Usage: make <command>'
	@echo
	@echo 'where <command> is one of the following:'
	@echo
	@grep -E '^[a-z0-9A-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo
.DEFAULT_GOAL := help


# @echo "activating google cloud secrets manager (rerun if fails)"
# @gcloud services enable secretmanager.googleapis.com
# @echo ${DOCKER_LOGIN} | gcloud secrets update docker-login --data-file=- \
# 		--replication-policy=user-managed \
# 		--locations=${GCP_REGION}
# @echo ${DOCKER_PASSWORD} | gcloud secrets create docker-password --data-file=- \
# 		--replication-policy=user-managed \
# 		--locations=${GCP_REGION}

# add-ssl-cert-tf: ## create and validate ssl certificate with terraform
# 	-@echo "attempting to create aws load balancer"; \
# 	cd terraform_ssl; \
# 	terraform init; \
# 	export TF_VAR_DEBUG=${DEBUG}; \
# 	export TF_VAR_service_name=${SERVICE_NAME}; \
# 	export TF_VAR_hosted_zone=${AWS_HOSTED_ZONE}; \
# 	export TF_VAR_hosted_zone_id=${AWS_HOSTED_ZONE_ID}; \

# 	terraform plan

# gcloud secrets create SECRET [--data-file=PATH] [--labels=[KEY=VALUE,...]]
#     [--set-annotations=[KEY=VALUE,...]] [--topics=[TOPICS,...]]
#     [--expire-time=EXPIRE-TIME | --ttl=TTL]
#     [--next-rotation-time=NEXT_ROTATION_TIME
#       --rotation-period=ROTATION_PERIOD]
#     [--replication-policy-file=REPLICATION-POLICY-FILE
#       | --kms-key-name=KMS-KEY-NAME
#       --locations=[LOCATION,...] --replication-policy=POLICY]
#     [GCLOUD_WIDE_FLAG ...]

# gcloud secrets update SECRET [--etag=ETAG]
# [--update-labels=[KEY=VALUE,...]]
# [--add-topics=[ADD-TOPICS,...] | --clear-topics
#   | --remove-topics=[REMOVE-TOPICS,...]]
# [--clear-annotations | --remove-annotations=[KEY,...]
#   | --update-annotations=[KEY=VALUE,...]]
# [--clear-labels | --remove-labels=[KEY,...]]
# [--clear-version-aliases | --remove-version-aliases=[KEY,...]
#   | --update-version-aliases=[KEY=VALUE,...]]
# [--expire-time=EXPIRE-TIME | --remove-expiration | --ttl=TTL]
# [--next-rotation-time=NEXT_ROTATION_TIME --remove-next-rotation-time
#   --remove-rotation-period
#   --remove-rotation-schedule --rotation-period=ROTATION_PERIOD]
# [GCLOUD_WIDE_FLAG ...]


# [1]+  Stopped                 make start-FULL-REBUILD | ts '%H:%M:%S ||' | ts -s '%H:%M:%S ||'

# create-repos: ## create google cloud repos
# 	make verify-project
# 	make set-project
# 	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
# 	export GCP_REGION=${GCP_REGION}; \
# 	export GCP_PROJECT_ID=${GCP_PROJECT_ID}; \
# 	export DOCKER_REPO=${DOCKER_REPO}; \
# 	export DOCKER_LOGIN=${DOCKER_LOGIN}; \
# 	export DOCKER_PASSWORD=${DOCKER_PASSWORD}; \
# 	../bin/create_repos.py
# 	touch create-repos

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
