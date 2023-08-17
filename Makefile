## TTD:
# make start; make stop
# make PROD start; make PROD stop
# make TEST start; make TEST stop
# update TAG

SHELL=/bin/bash

BASEURL ?= https://127.0.0.1.sslip.io
E2E_RUN = cd e2e; CYPRESS_BASE_URL=$(BASEURL)
STATIC_FILES = static_files
export ENV_FILE = .env
export TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,""); print $$2}')
export GIT_HASH = $(shell git rev-parse --short HEAD)
export COMPOSE_FILE_ARGS = -f docker-compose.yml -f docker-compose.dev.yml

PROD: ## Run in prod mode (e.g. `make PROD start`, etc.)
	$(eval ENV_FILE = prod.env)
	$(eval TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval COMPOSE_FILE_ARGS = -f docker-compose.yml)

TEST: ## Run in test mode (e.g. `make TEST start`, etc.)
	$(eval ENV_FILE = test.env)
	$(eval TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval COMPOSE_FILE_ARGS = -f docker-compose.yml -f docker-compose.test.yml)

.PHONY: DEV-CLOUD
DEV-CLOUD: ## Run in test mode (e.g. `make TEST start`, etc.)
	$(eval ENV_FILE = dev-cloud.env)
	@cd math && \
	/bin/rm -f .env && \
	ln -s ../${ENV_FILE} .env
	$(eval TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval GCP_BUCKET_NAME = $(shell grep -e ^GCP_BUCKET_NAME ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval GCP_PROJECT = $(shell grep -e ^GCP_PROJECT ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval GCP_BUCKET_LOCATION = $(shell grep -e ^GCP_BUCKET_LOCATION ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval COMPOSE_FILE_ARGS = -f docker-compose.yml -f docker-compose.test.yml)

echo_vars:
	@echo ENV_FILE=${ENV_FILE}
	@echo TAG=${TAG}

pull: echo_vars ## Pull most recent Docker container builds (nightlies)
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} pull

start: echo_vars ## Start all Docker containers
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up

stop: echo_vars ## Stop all Docker containers
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down

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

hash: ## Show current short hash
	@echo Git hash: ${GIT_HASH}

build: echo_vars ## [Re]Build all Docker containers
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build

build-no-cache: echo_vars ## Build all Docker containers without cache
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build --no-cache

start-recreate: echo_vars ## Start all Docker containers with recreated environments
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --force-recreate

start-rebuild: echo_vars ## Start all Docker containers, [re]building as needed
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --build

start-FULL-REBUILD: echo_vars stop rm-ALL ## Remove and restart all Docker containers, volumes, and images where (polis_tag="${TAG}")
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build --no-cache
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --build
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --build

cp-static-assets-docker-helper: # Deploy static assets locally
	@echo "One polis-file-server container found. Copying files...";
	@if [ -d "${STATIC_FILES}" ]; then \
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


e2e-install: e2e/node_modules ## Install Cypress E2E testing tools
	$(E2E_RUN) npm install

e2e-prepare: ## Prepare to run Cypress E2E tests
	@# Testing embeds requires a override of a file prior to build.
	cp e2e/cypress/fixtures/html/embed.html client-admin/embed.html

e2e-run-minimal: ## Run E2E tests: minimal (smoke test)
	$(E2E_RUN) npm run e2e:minimal

e2e-run-standalone: ## Run E2E tests: standalone (no credentials required)
	$(E2E_RUN) npm run e2e:standalone

e2e-run-secret: ## Run E2E tests: secret (credentials required)
	$(E2E_RUN) npm run e2e:secret

e2e-run-subset: ## Run E2E tests: filter tests by TEST_FILTER envvar (without browser exit)
	$(E2E_RUN) npm run e2e:subset

e2e-run-all: ## Run E2E tests: all
	$(E2E_RUN) npm run e2e:all


# Helpful CLI shortcuts
rbs: start-rebuild

%:
	@true

.PHONY: help pull start stop rm-containers rm-volumes rm-images rm-ALL hash build-no-cache start-rebuild \
  start-recreate restart-FULL-REBUILD e2e-install e2e-prepare e2e-run-minimal e2e-run-standalone e2e-run-secret \
  e2e-run-subset e2e-run-all

help:
	@echo 'Usage: make <command>'
	@echo
	@echo 'where <command> is one of the following:'
	@echo
	@grep -E '^[a-z0-9A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
