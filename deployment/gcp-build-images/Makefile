# use "cat -e -t -v Makefile" to see tabs and newlines

BASE_ENV ?= .env
PROD_ENV ?= prod.env
DEV_ENV ?= dev.env
DOCKER_ENV ?= docker_temp.env
GCP_BUILD_IMAGE_DIRECTORY ?= deployment/gcp-build-images

export ENV_FILE = /dev/null

DOCKER_COMPOSE_FILE = ../../docker-compose.yml

include ${BASE_ENV}
export $(shell sed 's/=.*//' ${BASE_ENV})

ifneq ($(MAKING_CLEAN),1)
	CMD:=$(shell /bin/rm clean)
	export MAKING_CLEAN=1
endif

clean:
	@echo "\nCleaning up"
	@-rm update-polis-config
	@-rm docker_temp.env
	@-rm verify-project
	@-rm set-project
	@-rm create-cloudbuild-file
	@-rm make-temp-repo-dir
	@-rm clone-repo
	@-rm copy-config-files
	@-touch clean

PROD: clean ## Run in prod mode (e.g. `make PROD start`, etc.)
	@echo "\nRunning in prod mode"
	$(eval ENV_FILE = prod.env)
	$(eval include ${ENV_FILE})
	$(eval export $(shell sed 's/=.*//' ${ENV_FILE}))

DEV: clean ## Run in dev mode (e.g. `make DEV start`, etc.)
	@echo "\nRunning in dev mode"
	$(eval ENV_FILE = dev.env)
	$(eval include ${ENV_FILE})
	$(eval export $(shell sed 's/=.*//' ${ENV_FILE}))

docker_env:
	@echo "\nCreating docker_temp.env file"
	$(shell cat ${BASE_ENV} > ${DOCKER_ENV})
	$(shell cat ${ENV_FILE} >> ${DOCKER_ENV})
	@touch docker_env

verify-project:
	@echo "\nverifying project"
	@if [ -z ${GCP_PROJECT_ID} ]; then \
		echo "ERROR: GCP_PROJECT_ID not set"; \
		exit 1; \
	fi
	@if ! gcloud projects list | grep -e ${GCP_PROJECT_ID}; then \
		echo "ERROR: project ${GCP_PROJECT_ID} does not exist"; \
		exit 1; \
	fi
	@touch verify-project

set-project: clean  # set google cloud project to value in DEV/PROD env
	@make verify-project
	@echo "\nsetting google project to ${GCP_PROJECT_ID}"
	@gcloud config set project ${GCP_PROJECT_ID}
	@touch set-project

make-temp-repo-dir: clean # create temp directory for repo clone
	@echo "\ncreating temp directory for repo clone"
	$(eval TEMP_REPO_DIR = $(shell mktemp -d))
	@echo ${TEMP_REPO_DIR} >> temp_repo_dirs.txt
	@ln -sf ${TEMP_REPO_DIR} .
	@touch make-temp-repo-dir

clone-repo: clean make-temp-repo-dir  ## create clean clone of repo
	@echo "\ncloning repo to ${TEMP_REPO_DIR}"
	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
		export TAG=${TAG}; \
		export GCP_REGION=${GCP_REGION}; \
		export GCP_PROJECT_ID=${GCP_PROJECT_ID}; \
		export GCP_PROJECT_NUMBER=${GCP_PROJECT_NUMBER}; \
		export DOCKER_REPO=${DOCKER_REPO}; \
		export DOCKER_LOGIN=${DOCKER_LOGIN}; \
		export DOCKER_PASSWORD=${DOCKER_PASSWORD}; \
		export TEMP_REPO_DIR=${TEMP_REPO_DIR}; \
		../bin/make_temp_repo_clone.py
	@echo "cloned repo to ${TEMP_REPO_DIR}"
	@touch clone-repo

copy-config-files: clean clone-repo # copy config files to temp repo dir
	@echo "\ncopying config files to ${TEMP_REPO_DIR}"
	@cd ../.. && \
		cp polis.config.js ${TEMP_REPO_DIR}/polis.config.js && \
		cp *.env ${TEMP_REPO_DIR}
	@touch copy-config-files

update-polis-config: clean copy-config-files # Copy polis.config.js to client-* directories
	@echo "\nUpdating polis.config.js in client-* directories"
	@echo "Copying polis.config.js (if present) to client-* directories"
	@echo "Renaming polis.config.template.js to polis.config.template.js.bak"
	@echo "Modifying client-*/Dockerfile(s)"
	@cd ${TEMP_REPO_DIR} && \
		cp polis.config.js client-participation; \
		cp polis.config.js client-admin; \
		cp polis.config.js client-report; \
		mv client-participation/polis.config.template.js \
			client-participation/polis.config.template.js.bak; \
		mv client-admin/polis.config.template.js \
			client-admin/polis.config.template.js.bak; \
		mv client-report/polis.config.template.js \
			client-report/polis.config.template.js.bak; \
		sed -i "" -e "s|COPY polis.config.template.js|#COPY polis.config.template.js|" \
			client-*/Dockerfile; \
		sed -i "" -e "s|COPY client-admin/polis.config.template.js|#COPY client-admin/polis.config.template.js|" \
			file-*/Dockerfile Dockerfile; \
		sed -i "" -e "s|COPY client-participation/polis.config.template.js|#COPY client-participation/polis.config.template.js|" \
			file-*/Dockerfile Dockerfile;
	@touch update-polis-config

create-cloudbuild-file: clean update-polis-config ## create cloudbuild.yaml file
	@echo "\ncreating cloudbuild.yaml file"
	@make verify-project
	@make set-project
	@cd ${TEMP_REPO_DIR} && \
		cd ${GCP_BUILD_IMAGE_DIRECTORY} && \
		export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
		export TAG=${TAG}; \
		export GCP_REGION=${GCP_REGION}; \
		export GCP_PROJECT_ID=${GCP_PROJECT_ID}; \
		export GCP_PROJECT_NUMBER=${GCP_PROJECT_NUMBER}; \
		export DOCKER_REPO=${DOCKER_REPO}; \
		export DOCKER_LOGIN=${DOCKER_LOGIN}; \
		export DOCKER_PASSWORD=${DOCKER_PASSWORD}; \
		../bin/create_cloudbuild_file.py; \
		cd ../..; \
		ln -sf ${GCP_BUILD_IMAGE_DIRECTORY}/cloudbuild.yaml .
	@touch create-cloudbuild-file

build-images: clean create-cloudbuild-file ## build docker images
	@echo "\nbuilding docker images"
	@echo "building docker images"
	@cd ${TEMP_REPO_DIR}; \
		gcloud builds submit \
				--region=${GCP_REGION} \
				--config=deployment/gcp-build-images/cloudbuild.yaml 2>&1 | \
			ts " %H:%M:%S ||" | ts -s "%.s ||"
	@echo "done building docker images"
	@echo "deleting temp repo clone at ${TEMP_REPO_DIR}"
	@/bin/rm -rf ${TEMP_REPO_DIR}
	@echo "deleting temp repo link at ${TEMP_REPO_DIR}"
	@/bin/rm `basename ${TEMP_REPO_DIR}`

rm-temp-repo-dirs: make-temp-repo-dir ## remove temp directories and links
	@make clean
	@echo "\nremoving temp directories for repo clone"
	@-base1=`dirname ${TEMP_REPO_DIR}`; \
		/bin/rm -rf $${base1}/tmp.*
	@echo "removing temp links for repo clone"
	@-/bin/rm tmp.*

echo_vars: clean docker_env
	@echo TAG=${TAG}

help:
	@echo 'Usage:  make <command>'
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
# 	@touch create-repos

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
# 	@touch authorize-dockerhub
