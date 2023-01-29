#!/usr/bin/env python3

import yaml
import sys
import os
import pprint

import boto3
from botocore.config import Config

# from common import ssl_certificate_arn, stack_description, logical_to_physical_id
from common import unique_values, extract_tag, add_elements_to_item, \
    update_keys, delete_keys

try:
    old_filename = os.environ["CLOUD_COMPOSE_FILE"]
    new_filename = os.environ["EDITED_CLOUD_COMPOSE_FILE"]
    billing_tag = os.environ["BILLING_TAG"]
    service_name = os.environ["SERVICE_NAME"]
    aws_region = os.environ["AWS_REGION"]
    aws_hosted_zone = os.environ["AWS_HOSTED_ZONE"]
except KeyError as err:
    print("ERROR: missing environment variable!")
    print(err)
    sys.exit()

# certificate_arn = ssl_certificate_arn(service_name, aws_hosted_zone)
# my_description = stack_description(stack_name)
# listener_arn = logical_to_physical_id(my_description, "Listener")[0]

with open(old_filename, "r") as stream:
    try:
        dictionary = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit()

new_elements = {"billing_tag": billing_tag}
add_elements_to_item("Tags", dictionary, new_elements)

replacement_values = {
    "ClusterName": service_name,
    "LogGroupName": f"/docker-compose/{service_name}",
}
#     "Vpc": {"Ref": "VPC"},
#     "VpcId": {"Ref": "VPC"},
# }
update_keys(dictionary, replacement_values)

with open(new_filename, 'w') as outfile:
    yaml.dump(dictionary, outfile, default_flow_style=False)

my_config = Config(
    region_name = aws_region,
)
ec2_client = boto3.client('ec2', config=my_config)

# Retrieves availability zones only for region of the ec2 object
response = ec2_client.describe_availability_zones()
availability_zones = [
    zone['ZoneName'] for zone in response['AvailabilityZones']]

if False: # delete all EFS file systems
    efs_client = boto3.client('efs', config=my_config)
    response = efs_client.describe_file_systems()
    file_system_ids = [
        filesystem['FileSystemId']
        for filesystem in response['FileSystems']]
    for file_system_id in file_system_ids:
        response = efs_client.delete_file_system(
            FileSystemId=file_system_id
        )
        print(file_system_id)
        print(response)

# project_value = extract_tag("com.docker.compose.project", dictionary)
# new_elements = {
#     "VPC": {
#         "Type": "AWS::EC2::VPC",
#         "Properties": {
#             "CidrBlock": "172.31.0.0/16",
#             "EnableDnsHostnames": True,
#             "EnableDnsSupport": True,
#             "Tags": [
#                 {"Key": "com.docker.compose.project", "Value": project_value},
#                 {"Key": "billing_tag", "Value": billing_tag},
#             ]
#     }}}
# add_elements_to_item("Resources", dictionary, new_elements)

# my_config = Config(
#     region_name = aws_region,
# )
# ec2_client = boto3.client('ec2', config=my_config)

# # Retrieves availability zones only for region of the ec2 object
# response = ec2_client.describe_availability_zones()
# availability_zones = [
#     zone['ZoneName'] for zone in response['AvailabilityZones']]

# cidr_blocks = [
#     "172.31.48.0/20",
#     "172.31.32.0/20",
#     "172.31.16.0/20",
#     "172.31.0.0/20",
# ]

# data = zip(
#     [i for i in range(0, len(availability_zones))],
#     availability_zones,
#     cidr_blocks)

# new_subnet_list = []
# for i, availability_zone, cidr_block in data:
#     new_subnet_list.append(f"Subnet{i}")
#     new_elements = {
#         f"Subnet{i}": {
#             "Type": "AWS::EC2::Subnet",
#             "Properties": {
#                 "AvailabilityZone": availability_zone,
#                 "CidrBlock": cidr_block,
#                 "VpcId": {"Ref": "VPC"},
#                 "Tags": [
#                     {"Key": "com.docker.compose.project", "Value": project_value},
#                     {"Key": "billing_tag", "Value": billing_tag},
#                 ]
#         }}}
#     add_elements_to_item("Resources", dictionary, new_elements)


# old_subnet_list = unique_values("SubnetId", dictionary)

