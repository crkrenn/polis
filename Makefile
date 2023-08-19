## TTD:
# make start; make stop
# make PROD start; make PROD stop
# make TEST start; make TEST stop
# update TAG

# CYPRESS_BASE_URL=

export SHELL = /bin/bash
export E2E_RUN = cd e2e;
export STATIC_FILES = static_files
export SERVER_IMAGE_NAME = polis-server
export CLOUD_BUILD_COMMAND = buildx build
export CLOUD_BUILD_OPTIONS = --platform linux/amd64

export ENV_FILE = .env
export TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,""); print $$2}')
export GIT_HASH = $(shell git rev-parse --short HEAD)
export COMPOSE_FILE_ARGS = -f docker-compose.yml -f docker-compose.dev.yml
# export CONTAINER_LIST =
export DOCKER_COMPOSE = docker compose

USE_DOCKER-COMPOSE: # use docker-compose
	$(eval DOCKER_COMPOSE = docker-compose)

SERVER_ONLY: # start server and nginx containers only
	$(eval CONTAINER_LIST = server nginx-proxy)
	@echo "CONTAINER_LIST=${CONTAINER_LIST}"

MATH_ONLY: # start math container only
	$(eval CONTAINER_LIST = math)
	@echo "CONTAINER_LIST=${CONTAINER_LIST}"

ALL_BUT_MATH: # start all containers except math
	$(eval CONTAINER_LIST = server postgres file-server nginx-proxy)
	@echo "CONTAINER_LIST=${CONTAINER_LIST}"

PROD: ## Run in prod mode (e.g. `make PROD start`, etc.)
	$(eval ENV_FILE = prod.env)
	$(eval TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval COMPOSE_FILE_ARGS = -f docker-compose.yml)

TEST: ## Run in test mode (e.g. `make TEST start`, etc.)
	$(eval ENV_FILE = test.env)
	@cd math && \
	/bin/rm -f .env && \
	ln -s ../${ENV_FILE} .env
	$(eval TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval COMPOSE_FILE_ARGS = -f docker-compose.yml -f docker-compose.test.yml)

.PHONY: DEV-CLOUD
DEV-CLOUD: ## Run with DEV-CLOUD settings (e.g. `make DEV-CLOUD start`, etc.)
	$(eval ENV_FILE = dev-cloud.env)
	@cd math && \
	/bin/rm -f .env && \
	ln -s ../${ENV_FILE} .env
	$(eval TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval GCP_BUCKET_NAME = $(shell grep -e ^GCP_BUCKET_NAME ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval GCP_PROJECT = $(shell grep -e ^GCP_PROJECT ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval GCP_BUCKET_LOCATION = $(shell grep -e ^GCP_BUCKET_LOCATION ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval GCP_CLOUD_RUN_REGION = $(shell grep -e ^GCP_CLOUD_RUN_REGION ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval COMPOSE_FILE_ARGS = -f docker-compose.yml -f docker-compose.test.yml)

echo_vars:
	@echo ENV_FILE=${ENV_FILE}
	@echo TAG=${TAG}

### (section break)

pull: echo_vars ## Pull most recent Docker container builds (nightlies)
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} pull ${CONTAINER_LIST}

start: echo_vars ## Start all Docker containers
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up ${CONTAINER_LIST}

stop: echo_vars ## Stop all Docker containers
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down ${CONTAINER_LIST}

rm-containers: echo_vars ## Remove Docker containers where (polis_tag="${TAG}")
	@echo 'removing filtered containers (polis_tag="${TAG}")'
	@-docker rm -f $(shell docker ps -aq --filter "label=polis_tag=${TAG}")

rm-volumes: echo_vars ## Remove Docker volumes where (polis_tag="${TAG}")
	@echo 'removing filtered volumes (polis_tag="${TAG}")'
	@-docker volume rm -f $(shell docker volume ls -q --filter "label=polis_tag=${TAG}")

rm-images: echo_vars ## Remove Docker images where (polis_tag="${TAG}")
	@echo 'removing filtered images (polis_tag="${TAG}")'
	@-docker rmi -f $(shell docker images -q --filter "label=polis_tag=${TAG}")

rm-ALL: rm-containers rm-volumes rm-images ## Remove Docker containers, volumes, and images where (polis_tag="${TAG}")
	@echo Done.

rm-single-image: ## Remove Docker image that matches REGEXP (e.g. make rm-single-image REGEXP='file-server.*test')
	@if [ "$(REGEXP)" = "" ]; then \
		echo "REGEXP is not defined"; \
		echo "Please use: make rm-single-image REGEXP='file-server.*test'"; \
		exit 1; \
	fi
	@MATCH_COUNT=$$(docker images | grep -E "$(REGEXP)" | wc -l); \
	if [ "$$MATCH_COUNT" -gt 1 ]; then \
		echo "Error: REGEXP matches more than one image"; \
		exit 1; \
	elif [ "$$MATCH_COUNT" -eq 0 ]; then \
		echo "No matching images found."; \
		exit 0; \
	else \
		echo "REGEXP: $(REGEXP)"; \
		docker-compose down; \
		docker images \
		| grep -E "$(REGEXP)" \
		| awk '{print $$3}' \
		| xargs docker rmi 2>&1 \
		| awk '{print $$NF}' \
		| xargs docker rm; \
		docker images \
		| grep -E "$(REGEXP)" \
		| awk '{print $$3}' \
		| xargs docker rmi; \
	fi

### (section break)

build: echo_vars ## [Re]Build all Docker containers
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build ${CONTAINER_LIST}

build-no-cache: echo_vars ## Build all Docker containers without cache
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build --no-cache ${CONTAINER_LIST}

start-recreate: echo_vars ## Start all Docker containers with recreated environments
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --force-recreate ${CONTAINER_LIST}

start-rebuild: echo_vars ## Start all Docker containers, [re]building as needed
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --build ${CONTAINER_LIST}

start-FULL-REBUILD: echo_vars stop rm-ALL ## Remove and restart all Docker containers, volumes, and images where (polis_tag="${TAG}")
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build --no-cache ${CONTAINER_LIST}
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down ${CONTAINER_LIST}
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --build ${CONTAINER_LIST}
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down ${CONTAINER_LIST}
	${DOCKER_COMPOSE} ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --build ${CONTAINER_LIST}

### (section break)

cp-static-assets-docker-helper: 
	@echo "One polis-file-server container found. Copying files...";
	@if [ -z "${STATIC_FILES}" ]; then \
		echo "Error: STATIC_FILES is not defined."; \
		exit 1; \
	elif [ -d "${STATIC_FILES}" ]; then \
		cd ${STATIC_FILES}; \
	else \
		mkdir ${STATIC_FILES} && cd ${STATIC_FILES}; \
	fi; \
	/bin/rm -rf * && \
	touch README.md && \
	cd .. && \
	CONTAINER_ID=$$(docker ps | grep 'polis-file-server' | awk '{print $$1}') && \
	echo "CONTAINER_ID=$${CONTAINER_ID}" && \
	docker cp $${CONTAINER_ID}:/app/build ${STATIC_FILES}/ && \
	cd ${STATIC_FILES}/build && \
	mv * .. && \
	cd .. && \
	rmdir build && \
	cd .. && \
	make gunzip-nonsuffix-files DIR=${STATIC_FILES}

gunzip-nonsuffix-files:
	@cd ${DIR} && find . -type f ! -name "*.gz" -print | while read -r file; do \
		if file "$$file" | grep -q "gzip compressed"; then \
			echo "Gunzipping $$file"; \
			gunzip -c "$$file" > "$$file.unzipped" && mv "$$file.unzipped" "$$file"; \
		fi \
	done

cp-static-assets-docker: ## Copy static assets from polis-file-server container to STATIC_FILES directory
	$(eval CONTAINER_COUNT=$(shell docker ps | grep 'polis-file-server' | wc -l))
	@if [ "$(CONTAINER_COUNT)" -eq "0" ]; then \
		echo "No polis-file-server containers found. Exiting."; \
	elif [ "$(CONTAINER_COUNT)" -eq "1" ]; then \
		make cp-static-assets-docker-helper; \
	else \
		echo "Multiple polis-file-server containers found. Exiting."; \
	fi

serve-static-assets: ## Serve static assets
	cd ${STATIC_FILES} && \
	python -m http.server 8080

upload-gcp-static-assets: create-gcp-bucket ## Upload static assets to GCP bucket
	gsutil -m cp -r ${STATIC_FILES}/* gs://${GCP_BUCKET_NAME}/

create-gcp-bucket: # Create GCP bucket if it doesn't exist
	@if [ -z "$(GCP_BUCKET_NAME)" ]; then \
		echo "Error: GCP_BUCKET_NAME is not defined."; \
		exit 1; \
	fi
	@if [ -z "$(GCP_PROJECT)" ]; then \
		echo "Error: GCP_PROJECT is not defined."; \
		exit 1; \
	fi
	@if [ -z "$(GCP_BUCKET_LOCATION)" ]; then \
		echo "Error: GCP_BUCKET_LOCATION is not defined."; \
		exit 1; \
	fi
	@BUCKET_URL=gs://$(GCP_BUCKET_NAME); \
	if ! gsutil ls $$BUCKET_URL 1>/dev/null 2>&1; then \
		gsutil mb -p $(GCP_PROJECT) -l $(GCP_BUCKET_LOCATION) $$BUCKET_URL && \
		echo "Bucket $(GCP_BUCKET_NAME) created successfully."; \
	else \
		echo "Bucket $(GCP_BUCKET_NAME) already exists."; \
	fi && \
	gsutil iam ch allUsers:objectViewer $$BUCKET_URL

### (section break)

run-docker-server-locally: # Run dockerized server locally
	@echo "Running dockerized server locally..."
	@echo "To stop, press Ctrl+C"
	${DOCKER_COMPOSE} -f docker-compose.server.yml --env-file ${ENV_FILE} up

upload-gcp-docker-server: ## Build and upload dockerized server to google cloud
	@if [ -z "$(GCP_PROJECT)" ]; then \
		echo "Error: GCP_PROJECT is not defined."; \
		exit 1; \
	fi
	$(eval TIMESTAMP = $(shell date +"%Y-%m-%d--%H-%M-%S%z"))
	gcloud auth configure-docker
	docker ${CLOUD_BUILD_COMMAND} ${CLOUD_BUILD_OPTIONS} -t compdem/${SERVER_IMAGE_NAME}-amd64:${TAG} server
	docker tag compdem/${SERVER_IMAGE_NAME}-amd64:${TAG} gcr.io/${GCP_PROJECT}/${SERVER_IMAGE_NAME}:${TIMESTAMP}
	docker tag compdem/${SERVER_IMAGE_NAME}-amd64:${TAG} gcr.io/${GCP_PROJECT}/${SERVER_IMAGE_NAME}:latest
	docker push gcr.io/${GCP_PROJECT}/${SERVER_IMAGE_NAME}:${TIMESTAMP}
	docker push gcr.io/${GCP_PROJECT}/${SERVER_IMAGE_NAME}:latest

list-gcp-docker-images: ## List docker images in google cloud
	@if [ -z "$(GCP_PROJECT)" ]; then \
		echo "Error: GCP_PROJECT is not defined."; \
		exit 1; \
	fi
	@gcloud container images list-tags gcr.io/${GCP_PROJECT}/${SERVER_IMAGE_NAME}
	@echo to delete images, use:
	@echo gcloud container images delete gcr.io/${GCP_PROJECT}/${SERVER_IMAGE_NAME}:TAG_NAME

list-gcp-services: ## List cloud run services in google cloud
	gcloud run services list --platform managed --region ${GCP_CLOUD_RUN_REGION}

env-to-gcloud:
	$(eval GCLOUD_ENV_VARS=$(shell python bin/load_env_to_gcloud.py ${ENV_FILE}))
	@echo "GCLOUD_ENV_VARS=${GCLOUD_ENV_VARS}"

deploy-gcp-docker-server: env-to-gcloud ## Deploy latest dockerized server to google cloud
	@if [ -z "$(GCP_PROJECT)" ]; then \
		echo "Error: GCP_PROJECT is not defined."; \
		exit 1; \
	fi
	@gcloud services enable run.googleapis.com
	@gcloud run deploy ${SERVER_IMAGE_NAME} \
		--image gcr.io/${GCP_PROJECT}/${SERVER_IMAGE_NAME}:latest \
		--platform managed \
		--region ${GCP_CLOUD_RUN_REGION} \
		--allow-unauthenticated \
		--set-env-vars ${GCLOUD_ENV_VARS}

### (section break)

e2e-install: e2e/node_modules ## Install Cypress E2E testing tools
	$(E2E_RUN) npm install

e2e-run: ## Run E2E tests except those which require 3rd party services
	$(E2E_RUN) npm run test

e2e-run-all: ## Run E2E tests: all
	$(E2E_RUN) npm run e2e:all

e2e-run-interactive: ## Run E2E tests interactively
	$(E2E_RUN) npx cypress open

### (section break)

hash: ## Show current short hash
	@echo Git hash: ${GIT_HASH}

# Helpful CLI shortcuts
rbs: start-rebuild

all-help: ## Show extra make targets
	@echo 'Usage: make <command>'
	@echo
	@echo 'where <command> is one of the following:'
	@echo
	@grep -E '^[a-z0-9A-Z_-]+:.*?##? .*$$|###' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?##? "}; {if ($$0 ~ /###/) {print ""} else {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}}'

%:
	@true

.PHONY: help pull start stop rm-containers rm-volumes rm-images rm-ALL hash build-no-cache start-rebuild \
  start-recreate restart-FULL-REBUILD e2e-install e2e-run e2e-run-all e2e-run-some

help:
	@echo 'Usage: make <command>'
	@echo
	@echo 'where <command> is one of the following:'
	@echo
	@grep -E '^[a-z0-9A-Z_-]+:.*?## .*$$|###' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {if ($$0 ~ /###/) {print ""} else {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}}'



.DEFAULT_GOAL := help
