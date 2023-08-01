#!/usr/bin/env python3

import sys
import os
import yaml
# import subprocess
import pprint
import tempfile

try:
    DOCKER_COMPOSE_FILE = os.environ["DOCKER_COMPOSE_FILE"]
    TAG = os.environ["TAG"]
    GCP_REGION = os.environ["GCP_REGION"]
    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    DOCKER_REPO = os.environ["DOCKER_REPO"]
    DOCKER_LOGIN = os.environ["DOCKER_LOGIN"]
    DOCKER_PASSWORD = os.environ["DOCKER_PASSWORD"]
except KeyError as err:
    print("ERROR: missing environment variable!")
    print(err)
    sys.exit()

docker_compose = yaml.load(open(DOCKER_COMPOSE_FILE, "r"), Loader=yaml.FullLoader)

services = docker_compose["services"].keys()

images = []
for service in services:
    image = docker_compose["services"][service]["image"]
    image = image.replace('${DOCKER_REPO}/',
        f'gcr.io/{GCP_PROJECT_ID}/')
    image = image.replace(':${TAG}', f':{TAG}')
    context = docker_compose["services"][service]["build"]["context"]
    dockerfile = docker_compose["services"][service]["build"]["dockerfile"]
    dockerfile = os.path.join(context, dockerfile)
    images.append({
        "context": docker_compose["services"][service]["build"]["context"],
        "dockerfile": dockerfile,
        "image": image
    })

# steps:
# - name: 'gcr.io/cloud-builders/docker'
#   args: [ 'build', '-t', 'us-west2-docker.pkg.dev/$PROJECT_ID/quickstart-docker-repo/quickstart-image:tag1', '.' ]
# images:
# - 'us-west2-docker.pkg.dev/$PROJECT_ID/quickstart-docker-repo/quickstart-image:tag1'


build_steps = []
# build_steps.append({
#     "name": "gcr.io/cloud-builders/docker",
#     "entrypoint": "bash",
#     "args": ["-c", "docker login --username=$$docker-login --password=$$docker-password"],
#     "secretEnv": ["docker-login", "docker-password"]
# })

image_list = []
for image in images:
    try:
        os.symlink(
            os.path.join(os.path.dirname(DOCKER_COMPOSE_FILE),image["context"]),
            image["context"])
    except FileExistsError:
        pass
    build_steps.append({
        "name": "gcr.io/cloud-builders/docker",
        "entrypoint": "bash",
        "args": ["-c", f"docker build -t {image['image']} {image['context']} -f {image['dockerfile']}"],
        "waitFor": ['-'],  # The '-' indicates that this step begins immediately.
    })
    image_list.append(image["image"])
    # build_steps.append({
    #     "name": "gcr.io/cloud-builders/docker",
    #     "entrypoint": "bash",
    #     "args": ["-c", f"docker push {image['image']}"]
    # })

build_dict = {
    "steps": build_steps,
    "images": image_list,
    # "availableSecrets": {
    #     "secretManager": [
    #         {
    #         "versionName": f"projects/{GCP_PROJECT_ID}/secrets/docker-login/versions/latest",
    #         "env": 'docker-login'},
    #         {
    #         "versionName": f"projects/{GCP_PROJECT_ID}/secrets/docker-password/versions/latest",
    #         "env": 'docker-password'}]
    # },
}

# Write dict to file as yaml
with open('cloudbuild.yaml', 'w') as file:
    yaml.dump(build_dict, file, sort_keys=False)

# print(f"Beginning build of images")
# cmd = (f"gcloud artifacts repositories create {image} --repository-format=docker "
#         f"--location={GCP_REGION} --description=\"Docker repository\"")
# result = subprocess.run(cmd, shell=True, capture_output=True)