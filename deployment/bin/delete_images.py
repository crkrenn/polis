#!/usr/bin/env python3

import sys
import os
import yaml
import subprocess
import pprint

from common import call_cmd

import logging
import datetime

class DeltaTimeFormatter(logging.Formatter):
    def format(self, record):
        duration = datetime.datetime.utcfromtimestamp(record.relativeCreated / 1000)
        record.delta = duration.strftime("%H:%M:%S")
        return super().format(record)

# add custom formatter to root logger
handler = logging.StreamHandler()
LOGFORMAT = '+%(delta)s - %(asctime)s - %(module)s %(levelname)-9s: %(message)s'
fmt = DeltaTimeFormatter(LOGFORMAT)
handler.setFormatter(fmt)
logging.getLogger().addHandler(handler)

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

LOG.info("Deleting images")
for service in services:
    image = docker_compose["services"][service]["image"]
    image = image.replace('${DOCKER_REPO}/',
        f'{IMAGE_REPO}/')
    image = image.replace(':${TAG}', f':{TAG}')
    # LOG.info(f"Deleting {image}")
    cmd = (f"gcloud container images delete {image} --quiet --force-delete-tags")
    try:
        result = call_cmd(cmd)
    except subprocess.CalledProcessError as err:
        print
        if "is not a valid name" in err.output:
            LOG.info("Image not found, skipping")
            pass
        else:
            raise err
LOG.info(f"Done deleting images")
