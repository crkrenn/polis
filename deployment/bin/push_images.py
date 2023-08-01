#!/usr/bin/env python3

import sys
import os
import yaml
import subprocess
import pprint

from common import call_cmd
import delta_log_formatter

import logging
import datetime

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

try:
    DOCKER_COMPOSE_FILE = os.environ["DOCKER_COMPOSE_FILE"]
    IMAGE_REPO = os.environ["IMAGE_REPO"]
    AWS_REGION = os.environ["AWS_REGION"]
    AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]
    TAG = os.environ["TAG"]
except KeyError as err:
    print("ERROR: missing environment variable!")
    print(err)
    sys.exit()

AWS_REPO = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"

docker_compose = yaml.load(open(DOCKER_COMPOSE_FILE, "r"), Loader=yaml.FullLoader)

services = docker_compose["services"].keys()

LOG.info("Pulling images")
for service in services:
    image = docker_compose["services"][service]["image"]
    image = image.replace('${DOCKER_REPO}/',
        f'{IMAGE_REPO}/')
    image = image.replace(':${TAG}', f':{TAG}')
    LOG.info(f"Pulling {image}")
    cmd = (f"docker pull {image}")
    result = call_cmd(cmd)
LOG.info(f"Done pulling images")

LOG.info(f"Logging into AWS ECR")
cmd = (
    f"docker login -u AWS -p $(aws ecr get-login-password --region {AWS_REGION}) {AWS_REPO}")
result = call_cmd(cmd)
LOG.info(f"Logged into AWS ECR")

# docker tag e9ae3c220b23 aws_account_id.dkr.ecr.region.amazonaws.com/my-repository:tag
LOG.info("Pushing images")
for service in services:
    image = docker_compose["services"][service]["image"]
    repo = image
    image = image.replace(':${TAG}', f':{TAG}')
    new_image = image
    image = image.replace('${DOCKER_REPO}/',
        f'{IMAGE_REPO}/')
    new_image = new_image.replace('${DOCKER_REPO}/',
        f'{AWS_REPO}/')
    repo = repo.replace('${DOCKER_REPO}/','')
    repo = repo.replace(':${TAG}', '')

    LOG.info(f"Pushing {new_image}")
    try:
        cmd = (f"aws --region {AWS_REGION} ecr create-repository --repository-name {repo}")
        result = call_cmd(cmd)
    except subprocess.CalledProcessError as err:
        if "RepositoryAlreadyExistsException" in err.output:
            LOG.info("Repository already exists")
            pass
        else:
            raise err
    cmd = (f"docker tag {image} {new_image}")
    result = call_cmd(cmd)
    cmd = (f"docker push {new_image}")
    result = call_cmd(cmd)
LOG.info("Done pushing images")

cmd = (
    f"aws ecr get-login-password --region {AWS_REGION} | "
    f"docker login --username AWS --password-stdin "
    f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com")
result = subprocess.run(cmd, shell=True, capture_output=True)
if result.returncode != 0:
    print("ERROR")
    print(result.stderr.decode("utf-8"))
    sys.exit()

# # steps:
# # - name: 'gcr.io/cloud-builders/docker'
# #   args: [ 'build', '-t', 'us-west2-docker.pkg.dev/$PROJECT_ID/quickstart-docker-repo/quickstart-image:tag1', '.' ]
# # images:
# # - 'us-west2-docker.pkg.dev/$PROJECT_ID/quickstart-docker-repo/quickstart-image:tag1'


# build_steps = []
# # build_steps.append({
# #     "name": "gcr.io/cloud-builders/docker",
# #     "entrypoint": "bash",
# #     "args": ["-c", "docker login --username=$$docker-login --password=$$docker-password"],
# #     "secretEnv": ["docker-login", "docker-password"]
# # })

# image_list = []
# for image in images:
#     try:
#         os.symlink(
#             os.path.join(os.path.dirname(DOCKER_COMPOSE_FILE),image["context"]),
#             image["context"])
#     except FileExistsError:
#         pass
#     build_steps.append({
#         "name": "gcr.io/cloud-builders/docker",
#         "entrypoint": "bash",
#         "args": ["-c", f"docker build -t {image['image']} {image['context']} -f {image['dockerfile']}"],
#         "waitFor": ['-'],  # The '-' indicates that this step begins immediately.
#     })
#     image_list.append(image["image"])
#     # build_steps.append({
#     #     "name": "gcr.io/cloud-builders/docker",
#     #     "entrypoint": "bash",
#     #     "args": ["-c", f"docker push {image['image']}"]
#     # })

# build_dict = {
#     "steps": build_steps,
#     "images": image_list,
#     # "availableSecrets": {
#     #     "secretManager": [
#     #         {
#     #         "versionName": f"projects/{GCP_PROJECT_ID}/secrets/docker-login/versions/latest",
#     #         "env": 'docker-login'},
#     #         {
#     #         "versionName": f"projects/{GCP_PROJECT_ID}/secrets/docker-password/versions/latest",
#     #         "env": 'docker-password'}]
#     # },
# }

# # Write dict to file as yaml
# with open('cloudbuild.yaml', 'w') as file:
#     yaml.dump(build_dict, file, sort_keys=False)

# print(f"Beginning build of images")
# cmd = (f"gcloud artifacts repositories create {image} --repository-format=docker "
#         f"--location={GCP_REGION} --description=\"Docker repository\"")
# result = subprocess.run(cmd, shell=True, capture_output=True)