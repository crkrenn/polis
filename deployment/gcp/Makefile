SHELL := /bin/bash # enables `source env.sh && YourCommand`

# Makefile variables:
POLIS_ROOT ?= $(shell cd ../..; pwd)
ENV_SECRETS ?=  ~/.polis/prod.env


# rule:
#     source env.sh && YourCommand

build-server: ## Build server docker image
	@echo 'Building server'
	@cd ${POLIS_ROOT}/server; \
		pwd
		docker buildx build --platform linux/amd64 -f Dockerfile -t gcr.io/polarization-dashboard-dev-1/main-dash:latest .
		# docker push gcr.io/polarization-dashboard-dev-1/main-dash:latest

%:
	@true

.PHONY: help

help:
	@echo 'Usage: make <command>'
	@echo
	@echo 'where <command> is one of the following:'
	@echo
	@grep -E '^[a-z0-9A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

# docker buildx build --platform linux/amd64 -f ./Dockerfile -t democracygps/maine-dash:testamd .
# docker tag "democracygps/maine-dash:testamd" "democracygps/maine-dash:latest"
# docker push  "democracygps/maine-dash:latest"
# aws ecs update-service  --cluster dash-app --service dash-app-service --region us-east-2  --force-new-deployment

# docker buildx build --platform linux/amd64 -f Dockerfile -t gcr.io/polarization-dashboard-dev-1/main-dash:latest .
# docker push gcr.io/polarization-dashboard-dev-1/main-dash:latest


