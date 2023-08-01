BASE_ENV ?= .env
PROD_ENV ?= prod.env
DEV_ENV ?= dev.env
DOCKER_ENV ?= docker_temp.env
DOCKER_COMPOSE_FILE ?= ../../docker-compose.yml

CLOUD_COMPOSE_FILE = cloud-compose.yaml
EDITED_CLOUD_COMPOSE_FILE = cloud-compose-edit.yaml
TEMP_JSON_FILE = temp.json
EDITED_DOCKER_COMPOSE_FILE = docker-compose-edit.yaml

export ENV_FILE = /dev/null
export GIT_HASH = $(shell git rev-parse --short HEAD)

include ${BASE_ENV}
export $(shell sed 's/=.*//' ${BASE_ENV})

PROD: ## Run in prod mode (e.g. `make PROD start`, etc.)
	@echo Running in prod mode
	$(eval ENV_FILE = prod.env)
	$(eval include ${ENV_FILE})
	$(eval export $(shell sed 's/=.*//' ${ENV_FILE}))
	@make docker_env

DEV: ## Run in dev mode (e.g. `make DEV start`, etc.)
	@echo Running in dev mode
	$(eval ENV_FILE = dev.env)
	$(eval include ${ENV_FILE})
	$(eval export $(shell sed 's/=.*//' ${ENV_FILE}))
	@make docker_env

export DOCKER_DETACHED=--detach

ATTACHED: ## Run docker in "attached" mode, with output from all containers streaming to the terminal
	$(eval undefine DOCKER_DETACHED)

docker_env:
	$(shell cat ${BASE_ENV} > ${DOCKER_ENV})
	$(shell cat ${ENV_FILE} >> ${DOCKER_ENV})

clean: ## reset push-images, so they will be rerun
	@rm -f push-images
	@rm -f ${DOCKER_ENV}

verify-project:
	@if [ -z ${GCP_PROJECT_ID} ]; then \
		echo "ERROR: GCP_PROJECT_ID not set"; \
		exit 1; \
	fi
	@if ! gcloud projects list | grep -e ${GCP_PROJECT_ID}; then \
		echo "ERROR: project ${GCP_PROJECT_ID} does not exist"; \
		exit 1; \
	fi

verify-aws-region:
	@if [ -z ${AWS_REGION} ]; then \
		echo "ERROR: AWS_REGION not set"; \
		exit 1; \
	fi

delete-gcp-images: ## delete gcp images
	@make verify-project
	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
	export TAG=${TAG}; \
	export IMAGE_REPO=${IMAGE_REPO}; \
	export AWS_REGION=${AWS_REGION}; \
	docker context use ${LOCAL_DOCKER_CONTEXT}; \
	../bin/delete_gcp_images.py

push-images: ## push images to AWS ECR
	@make verify-project
	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
	export TAG=${TAG}; \
	export IMAGE_REPO=${IMAGE_REPO}; \
	export AWS_REGION=${AWS_REGION}; \
	docker context use ${LOCAL_DOCKER_CONTEXT}; \
	../bin/push_images.py
	touch push-images

start-local: docker_env echo_vars ## Start all Docker containers on local machine
	docker context use ${LOCAL_DOCKER_CONTEXT}; \
	docker-compose --env-file ${DOCKER_ENV} up ${DOCKER_DETACHED}

stop-local: docker_env echo_vars ## Start all Docker containers on local machine
	docker context use ${LOCAL_DOCKER_CONTEXT}; \
	docker-compose --env-file ${DOCKER_ENV} down

stop-ALL:  ## Stop all running containers
	@-docker container stop $(shell docker container ls -q)

build-docker-compose: docker_env ## build docker-compose
	@make verify-project
	@export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
	export GCP_REGION=${GCP_REGION}; \
	export GCP_PROJECT_ID=${GCP_PROJECT_ID}; \
	export IMAGE_REPO=${IMAGE_REPO}; \
	export TAG=${TAG}; \
	../bin/build_docker_compose.py

docker-login-aws: ## login to AWS ECR
	make verify-aws-region
	@echo logging into AWS ECR in ${AWS_REGION} region
	docker login -u AWS -p $(shell aws ecr get-login-password --region ${AWS_REGION}) ${AWS_REPO}


# docker-compose-edit: verify-aws-region ## update cloud compose file with custom features
# 	export DEBUG=${DEBUG}; \
# 	export DOCKER_COMPOSE_FILE=${DOCKER_COMPOSE_FILE}; \
# 	export EDITED_DOCKER_COMPOSE_FILE=${EDITED_DOCKER_COMPOSE_FILE}; \
# 	export BILLING_TAG=${BILLING_TAG}; \
# 	export SERVICE_NAME=${SERVICE_NAME}; \
# 	export AWS_REGION=${AWS_REGION}; \
# 	export AWS_HOSTED_ZONE=${AWS_HOSTED_ZONE}; \
# 	../bin/update_docker_compose.py

cloud-compose: docker-login-aws docker_env ## convert docker file to cloud compose file
	@export AWS_REGION=${AWS_REGION}; \
	docker context use ${CLOUD_DOCKER_CONTEXT}; \
	docker compose \
		--env-file ${DOCKER_ENV} \
		convert > ${CLOUD_COMPOSE_FILE}

cloud-compose-edit: cloud-compose ## update cloud compose file with custom features
	export DEBUG=${DEBUG}; \
	export CLOUD_COMPOSE_FILE=${CLOUD_COMPOSE_FILE}; \
	export EDITED_CLOUD_COMPOSE_FILE=${EDITED_CLOUD_COMPOSE_FILE}; \
	export BILLING_TAG=${BILLING_TAG}; \
	export SERVICE_NAME=${SERVICE_NAME}; \
	export AWS_REGION=${AWS_REGION}; \
	export AWS_HOSTED_ZONE=${AWS_HOSTED_ZONE}; \
	# export SSL_CERTIFICATE=`aws acm request-certificate \
	# 	--domain-name ${SERVICE_NAME}. \
	# 	--validation-method DNS | \
	# 	jq -r ".CertificateArn"` ; \
	../bin/update_cloud_compose.py

create-stack: cloud-compose-edit ## launch updated cloud compose file
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation create-stack \
		--stack-name ${SERVICE_NAME}-stack \
		--template-body file://${EDITED_CLOUD_COMPOSE_FILE} \
		--region ${AWS_REGION} \
		--capabilities CAPABILITY_IAM

update-stack: cloud-compose-edit ## update stack with current cloud compose file
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation update-stack \
		--stack-name ${SERVICE_NAME}-stack \
		--template-body file://${EDITED_CLOUD_COMPOSE_FILE} \
		--region ${AWS_REGION} \
		--capabilities CAPABILITY_IAM

describe-stack: verify-aws-region ## describe stack
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation list-stack-resources \
		--stack-name ${SERVICE_NAME}-stack \

stack-status: verify-aws-region ## summary of stack status
	@echo "All complete except:"
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation list-stack-resources \
		--stack-name ${SERVICE_NAME}-stack | \
	jq '.StackResourceSummaries[] | \
		select(.ResourceStatus | test("COMPLETE") | not)' | \
		grep -e LogicalResourceId -e ResourceStatus

noop:
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation list-stack-resources \
		--stack-name ${SERVICE_NAME}-stack | \
		grep -e ResourceStatus -e LogicalResourceId | \
		grep -v -B1 -e "COMPLETE"

stack-url: verify-aws-region ## get URL of stack load balancer
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation describe-stack-resource \
		--stack-name ${SERVICE_NAME}-stack \
		--logical-resource-id LoadBalancer | \
		jq '.StackResourceDetail.PhysicalResourceId' | \
		xargs aws elbv2 describe-load-balancers --load-balancer-arns | \
		jq -r '"http://" + (.LoadBalancers | .[0] | .DNSName)'

detect-stack-drift: cloud-compose-edit ## detect stack drift
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation detect-stack-drift \
		--stack-name ${SERVICE_NAME}-stack

show-stack-drift: cloud-compose-edit ## show stack drift summary
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation list-stack-resources \
		--stack-name ${SERVICE_NAME}-stack | \
		grep -e StackResourceDriftStatus -e LogicalResourceId | \
		grep -B1 -e "StackResourceDriftStatus.*MODIFIED" \
			-e "StackResourceDriftStatus.*NOT"

# restart-fileserver: verify-aws-region ## restart fileserver service
# 	@export AWS_REGION=${AWS_REGION}; \
# 	aws ecs update-service \
# 		--force-new-deployment \
# 		--service FileserverService \
# 		--cluster ${SERVICE_NAME}

# restart each service individually and all together
# ITEMS = item1 item2 item3

# # Define a target for each item
# $(ITEMS):
# 	# Recipe to run on each item
# 	echo "Running recipe on $@"
# 	# ...
# NUMBERS = 1 2 3 4
# doit:
#         $(foreach var,$(NUMBERS),./a.out $(var);)

        #   "PhysicalResourceId": "arn:aws:ecs:us-east-2:714774317425:service/polis3/polis3-stack-FileserverService-xha10PDWtslu",
        #     "PhysicalResourceId": "arn:aws:ecs:us-east-2:714774317425:service/polis3/polis3-stack-MathService-P7FCs9SDiBKT",
        #     "PhysicalResourceId": "arn:aws:ecs:us-east-2:714774317425:service/polis3/polis3-stack-NginxproxyService-XJGqZkHvTiEc",
        #     "PhysicalResourceId": "arn:aws:ecs:us-east-2:714774317425:service/polis3/polis3-stack-PostgresService-RpnL775hxJrM",
        #     "PhysicalResourceId": "arn:aws:ecs:us-east-2:714774317425:service/polis3/polis3-stack-ServerService-QCTbd7MYeoAt",

# restart-service: RESTART_SERVICE_VARIABLE = ${RESTART_SERVICE}
restart-service: verify-aws-region ## restart fileserver service
	@echo "Restarting: ${RESTART_SERVICE_VARIABLE}"
	@exit 1
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation list-stack-resources \
		--stack-name "${SERVICE_NAME}-stack" | \
	jq '.StackResourceSummaries[] | \
		select(.LogicalResourceId | test(${RESTART_SERVICE_VARIABLE})) | \
		select(.ResourceType | test("AWS::ECS::Service")) | \
		.PhysicalResourceId' | \
	xargs aws ecs update-service \
		--force-new-deployment \
		--cluster ${SERVICE_NAME} \
		--service

test1:
	$(eval RESTART_SERVICE_VARIABLE = test1)
	make restart-service

test2:
	$(eval RESTART_SERVICE_VARIABLE = test2)
	make restart-service


restart-fileserver: verify-aws-region ## describe stack
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation list-stack-resources \
		--stack-name "${SERVICE_NAME}-stack" | \
	jq '.StackResourceSummaries[] | \
		select(.LogicalResourceId | test("FileserverService")) | \
		select(.ResourceType | test("AWS::ECS::Service")) | \
		.PhysicalResourceId' | \
	xargs aws ecs update-service \
		--force-new-deployment \
		--cluster ${SERVICE_NAME} \
		--service

noop:
	jq '.StackResourceSummaries.[] | \
		select(.LogicalResourceId | test("^FileserverService$")) | \
		.PhysicalResourceId'
	aws cloudformation list-stack-resources \
		--stack-name ${SERVICE_NAME}-stack | \
		jq '.StackResourceSummaries.[] | \
		select(.LogicalResourceId | test("FileserverService"))'


	select(.LogicalResourceId | \
		test("FileserverService")) | .PhysicalResourceId'
		 | \
	xargs aws ecs update-service \
		--force-new-deployment \
		--cluster ${SERVICE_NAME} \
		--service


# make DEV describe-stack | jq -r ".StackResourceSummaries"

# aws ecs update-service --force-new-deployment --service my-service --cluster cluster-name
# FileserverService

delete-stack:  verify-aws-region ## delete running stack
	@export AWS_REGION=${AWS_REGION}; \
	aws cloudformation delete-stack --stack-name ${SERVICE_NAME}-stack

# FileserverService
#  # | select(.LogicalResourceId | test("FileserverService"))'

# '


# #!/usr/../bin/env make

# # TTD: add update stack
# # TTD: add certificate, etc.
# # add make for route53

# # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html
# # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listenercertificate.html
# #https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html

# DOT_ENV ?= .env
# PROD_ENV ?= prod.env
# DOCKER_ENV ?= docker_temp.env

# include ${DOT_ENV}
# export $(shell sed 's/=.*//' ${DOT_ENV})
# $(shell cat ${DOT_ENV} > ${DOCKER_ENV})

# ifneq ("$(wildcard $(PROD_ENV))","")
#   $(shell cat ${PROD_ENV} >> ${DOCKER_ENV})
#   include ${PROD_ENV}
#   export $(shell sed 's/=.*//' ${PROD_ENV})
# endif


# export DEBUG=false

# DEBUG: ## Run tools in DEBUG, with more diagnostic outputs
# 	$(eval DEBUG=true)

# # load_balancer:
# # 	-@echo "attempting to create aws load balancer"; \
# # 	cd terraform; \
# # 	terraform init; \
# #   export TF_VAR_DEBUG=${DEBUG}; \
# # 	export TF_VAR_service_name=${SERVICE_NAME}; \
# # 	export TF_VAR_hosted_zone=${AWS_HOSTED_ZONE}; \
# # 	export TF_VAR_s3_bucket=${S3_BUCKET}; \
# # 	export TF_VAR_billing_tag=${BILLING_TAG}; \
# # 	terraform plan

# add-ssl-cert-tf: ## create and validate ssl certificate with terraform
# 	-@echo "attempting to create aws load balancer"; \
# 	cd terraform_ssl; \
# 	terraform init; \
# 	export TF_VAR_DEBUG=${DEBUG}; \
# 	export TF_VAR_service_name=${SERVICE_NAME}; \
# 	export TF_VAR_hosted_zone=${AWS_HOSTED_ZONE}; \
# 	export TF_VAR_hosted_zone_id=${AWS_HOSTED_ZONE_ID}; \

# 	terraform plan

# dns_input:
# 	@jq --null-input \
# 	--arg user "${AWS_REGION}" \
# 	--arg password "${AWS_HOSTED_ZONE}" \
# 	'{ \
# 		"Comment": "CREATE/DELETE/UPSERT a record ", \
# 		"Changes": [{ \
# 		"Action": "CREATE", \
# 					"ResourceRecordSet": { \
# 								"Name": "a.example.com", \
# 								"Type": "A", \
# 								"TTL": 300, \
# 							"ResourceRecords": [{ "Value": "4.4.4.4"}] \
# 		}}] \
# 	}' > ${TEMP_JSON_FILE}; \
# 	cat ${TEMP_JSON_FILE}
# # $ aws route53 change-resource-record-sets --hosted-zone-id ZXXXXXXXXXX --change-batch file://sample.json

# # -import_dns:
# # -       -@echo "attempting to authenticate with aws dns"; \
# # -       cd terraform; \
# # -       terraform init; \
# #   export TF_VAR_DEBUG=${DEBUG}; \
# # -       export TFVAR_aws_root_domain=${AWS_ROOT_DOMAIN}; \
# # -       terraform import aws_route53_zone.root ${AWS_HOSTED_ZONE_ID}




# add-ssl-cert:  ## update-stack add ssl certificate to load balancer
# 	@export DEBUG=${DEBUG}; \
# 	export SERVICE_NAME=${SERVICE_NAME}; \
# 	export AWS_REGION=${AWS_REGION}; \
# 	export AWS_HOSTED_ZONE=${AWS_HOSTED_ZONE}; \
# 	export STACK_NAME=${SERVICE_NAME}-stack; \
# 	../bin/add_ssl_certificate.py

# noop:
# #   export TF_VAR_DEBUG=${DEBUG}; \
# 	export LOAD_BALANCER_ARN=`aws cloudformation list-stack-resources \
# 		--stack-name ${SERVICE_NAME}-stack`; \
# 	aws elbv2 add-listener-certificates \
# 	--listener-arn arn:aws:elasticloadbalancing:us-west-2:123456789012:listener/app/my-load-balancer/50dc6c495c0c9188/f2f7dc8efc522ab2 --certificates CertificateArn=arn:aws:acm:us-west-2:123456789012:certificate/5cc54884-f4a3-4072-80be-05b9ba72f705
# 	aws acm request-certificate  \
# 			@aws cloudformation list-stack-resources \
# 		--stack-name ${SERVICE_NAME}-stack \
# 	echo $$SSL_CERTIFICATE_ARN; \


# help:
# 	@echo 'Usage: make <command>'
# 	@echo
# 	@echo 'where <command> is one of the following:'
# 	@echo
# 	@grep -E '^[a-z0-9A-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
# 	@echo
# 	@echo 'Note: some targets (e.g. ATTACHED) require GNU Make version 3.82 or above.'
# .DEFAULT_GOAL := help

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