#!/usr/bin/env python3

import sys
import os
import yaml
import subprocess

try:
    docker_compose_file = os.environ["DOCKER_COMPOSE_FILE"]
    gcp_region = os.environ["GCP_REGION"]
    gcp_project_id = os.environ["GCP_PROJECT_ID"]
    docker_login = os.environ["DOCKER_LOGIN"]
    docker_password = os.environ["DOCKER_PASSWORD"]
except KeyError as err:
    print("ERROR: missing environment variable!")
    print(err)
    sys.exit()

docker_compose = yaml.load(open(docker_compose_file, "r"), Loader=yaml.FullLoader)

services = docker_compose["services"].keys()
images = [docker_compose["services"][service]["image"] for service in services]
images = [image.replace('${DOCKER_REPO}/', '') for image in images]
images = [image.replace(':${TAG}', '') for image in images]

for image in images:
    print(f"Creating repository for image: {image}")
    cmd = (f"gcloud artifacts repositories create {image} --repository-format=docker "
            f"--location={gcp_region} --description=\"Docker repository\"")
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        if "ALREADY_EXISTS" in result.stderr.decode("utf-8"):
            print(f"Repository {image} already exists")
        else:
            print(result.stderr.decode("utf-8"))
            sys.exit()
