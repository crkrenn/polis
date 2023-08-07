# Note: for diagnosing build performance, install "ts" from moreutils and:
# 	make <targets> | ts -s "%.s || %H:%M:%S ||"
## TTD:
# make start; make stop
# make PROD start; make PROD stop
# update TAG

SHELL=/bin/bash

BASEURL ?= https://127.0.0.1.sslip.io
E2E_RUN = cd e2e; CYPRESS_BASE_URL=$(BASEURL)
export ENV_FILE = .env
export TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,""); print $$2}')
export GIT_HASH = $(shell git rev-parse --short HEAD)
export COMPOSE_FILE_ARGS = -f docker-compose.yml -f docker-compose.dev.yml

# $(shell docker context use ${LOCAL_DOCKER_CONTEXT})

DETACHED: ## Run docker in "detached" mode
	$(eval DOCKER_DETACHED = --detach)

AMD: ## Build for linux/amd platform
	$(eval DOCKER_DEFAULT_PLATFORM = linux/amd64)

PROD: ## Run in prod mode (e.g. `make PROD start`, etc.)
	$(eval ENV_FILE = prod.env)
	$(eval TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval COMPOSE_FILE_ARGS = -f docker-compose.yml)

TEST: ## Run in test mode (e.g. `make TEST start`, etc.)
	$(eval ENV_FILE = test.env)
	$(eval TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval COMPOSE_FILE_ARGS = -f docker-compose.yml -f docker-compose.test.yml)

CRK: ## Run in crk mode (e.g. `make CRK start`, etc.)
	$(eval ENV_FILE = test.env)
	$(eval TAG = $(shell grep -e ^TAG ${ENV_FILE} | awk -F'[=]' '{gsub(/ /,"");print $$2}'))
	$(eval COMPOSE_FILE_ARGS = -f docker-compose.yml )

echo_vars:
	@echo ENV_FILE=${ENV_FILE}
	@echo TAG=${TAG}

pull: echo_vars ## Pull most recent Docker container builds (nightlies)
	docker-compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} pull

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

rm-ALL-ALL-TAGS: ## Remove EVERY Docker container, volume, and image on this machine
	-docker rm -f $(shell docker ps -aq)
	-docker rmi -f $(shell docker images -q)
	-docker volume rm $(shell docker volume ls -q)

hash: ## Show current short hash
	@echo Git hash: ${GIT_HASH}

build: echo_vars ## [Re]Build all Docker containers
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build

build-no-cache: echo_vars ## Build all Docker containers without cache
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build --no-cache

start-recreate: echo_vars ## Start all Docker containers with recreated environments
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --force-recreate

build-static-assets: ## Build static assets
	cd client-participation && \
	npm install webpack && \
	npm run build:prod
	cd client-admin && \
	npm install webpack && \
	npm run build:prod
	cd client-report && \
	npm install gulp && \
	npm run build:prod
	cd static_files && \
	/bin/rm -rf * && \
	touch README.md && \
	cd .. && \
	cp -r client-participation/dist/* static_files/ && \
	cp -r client-admin/build/* static_files/ && \
	cp -r client-report/dist/* static_files/ && \
	cd static_files && \
	ln -sf index.html index_admin.html

build-static-assets-dev: ## Build static assets
	cd client-participation && \
	npm install webpack && \
	npm run build:dev
	cd client-admin && \
	npm install webpack && \
	npm run build:dev
	cd client-report && \
	npm install gulp && \
	npm run build:prod

deploy-static-assets-local: ## Deploy static assets locally
	cd static_files && \
	/bin/rm -rf * && \
	touch README.md && \
	cd .. && \
	cp -r client-admin/build/* static_files/ && \
	cd static_files && \
	mv index.html index_admin.html && \
	cd .. && \
	cp -r client-participation/dist/* static_files/ && \
	cp -r client-report/dist/* static_files/

deploy-static-assets-docker: ## Deploy static assets locally
	@cd static_files && \
	/bin/rm -rf * && \
	touch README.md && \
	cd .. && \
	CONTAINER_ID=$$(docker ps | grep 'polis-file-server' | awk '{print $$1}') && \
	echo "CONTAINER_ID=$${CONTAINER_ID}" && \
	docker cp $${CONTAINER_ID}:/app/build static_files/ && \
	cd static_files/build && \
	mv * .. && \
	cd .. && \
	rmdir build

noop:
	cp -r client-admin/build/* static_files/ && \
	cd static_files && \
	mv index.html index_admin.html && \
	cd .. && \
	cp -r client-participation/dist/* static_files/ && \
	cp -r client-report/dist/* static_files/
serve-static-assets: ## Serve static assets
	cd static_files && \
	python -m http.server 8080


# @TTD: fix this; it doesn't work if DOCKER_DEFAULT_PLATFORM is not set
# start-rebuild: echo_vars ## Start all Docker containers, [re]building as needed
# 	@export DOCKER_DEFAULT_PLATFORM=${DOCKER_DEFAULT_PLATFORM}; \
# 		docker-compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up ${DOCKER_DETACHED}  --build

# start-FULL-REBUILD: echo_vars stop rm-ALL ## Remove and restart all Docker containers, volumes, and images where (polis_tag="${TAG}")
# 	@export DOCKER_DEFAULT_PLATFORM=${DOCKER_DEFAULT_PLATFORM}; \
# 		docker-compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build --no-cache
# 	docker-compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down
# 	@export DOCKER_DEFAULT_PLATFORM=${DOCKER_DEFAULT_PLATFORM}; \
# 		docker-compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --detach --build
# 	docker-compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down
# 	@export DOCKER_DEFAULT_PLATFORM=${DOCKER_DEFAULT_PLATFORM}; \
# 		docker-compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up ${DOCKER_DETACHED}  --build

start-rebuild: echo_vars ## Start all Docker containers, [re]building as needed
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --build

start-FULL-REBUILD: echo_vars stop rm-ALL ## Remove and restart all Docker containers, volumes, and images where (polis_tag="${TAG}")
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} build --no-cache
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --build
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} down
	docker compose ${COMPOSE_FILE_ARGS} --env-file ${ENV_FILE} up --build

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
	@grep -E '^[a-z0-9A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "Use 'make <target> | ts -s '%.s || %H:%M:%S ||' to diagnose build performance"
.DEFAULT_GOAL := help
