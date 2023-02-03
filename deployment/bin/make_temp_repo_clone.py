#!/usr/bin/env python3

import sys
import os
import yaml
import subprocess
import pprint
import tempfile

from common import call_cmd

# this import modifies the log format
import delta_log_formatter

import logging

LOG = logging.getLogger(__name__)
# LOG.addHandler(handler)
LOG.setLevel(logging.DEBUG)

try:
    DOCKER_COMPOSE_FILE = os.environ["DOCKER_COMPOSE_FILE"]
    TAG = os.environ["TAG"]
    GCP_REGION = os.environ["GCP_REGION"]
    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    DOCKER_REPO = os.environ["DOCKER_REPO"]
    DOCKER_LOGIN = os.environ["DOCKER_LOGIN"]
    DOCKER_PASSWORD = os.environ["DOCKER_PASSWORD"]
    TEMP_DIR = os.environ["TEMP_DIR"]
except KeyError as err:
    print("ERROR: missing environment variable!")
    print(err)
    sys.exit()

result = subprocess.run("git rev-parse --show-toplevel", shell=True, check=True, capture_output=True)
root_directory = result.stdout.decode("utf-8").strip()
LOG.info(f"Root directory: {root_directory}")

result = subprocess.run("git status", shell=True, check=True, capture_output=True)
if "Changes not staged for commit" in result.stdout.decode("utf-8"):
    LOG.error("Changes not staged for commit: please commit or stash before running this script")
    sys.exit()
if "no changes added to commit" in result.stdout.decode("utf-8"):
    LOG.info("No changes to commit")
else:
    LOG.error("Changes to commit: please commit or stash before running this script")
    sys.exit()
LOG.info(f"Root directory: {root_directory}")
"no changes added to commit"
# get branch name from git status
# verify that "nothing added to commit"
# clone repo
# copy links in root directory (dev.env, polis.config.json)
# verify that cloudignore is correct


# LOG.info(f"Pushing {new_image}")
# try:
#     cmd = (f"aws --region {AWS_REGION} ecr create-repository --repository-name {repo}")
#     result = call_cmd(cmd)
# except subprocess.CalledProcessError as err:
#     if "RepositoryAlreadyExistsException" in err.output:
#         LOG.info("Repository already exists")
#         pass
#     else:
#         raise err
# cmd = (f"docker tag {image} {new_image}")
# result = call_cmd(cmd)
# cmd = (f"docker push {new_image}")
# result = call_cmd(cmd)
