import boto3
import pydig
import copy
import subprocess
import datetime
import logging
import delta_log_formatter

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

def call_cmd(cmd):
    LOG.debug(cmd)
    # result = subprocess.run(cmd, shell=True, capture_output=True)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    while True:
        line = p.stdout.readline()
        if not line and p.poll() != None:
            break
        if line:
            stdout.append(line.decode("utf-8"))
            LOG.info(line.decode("utf-8").strip())
    if p.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=p.returncode,
            cmd=cmd,
            output="".join(stdout),
            stderr=None
            )
    return p


def dict_extract(key, var):
    if hasattr(var,'items'): # hasattr(var,'items') for python 3
        for k, v in var.items(): # var.items() for python 3
            if k == key:
                yield var
            if isinstance(v, dict):
                for result in dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in dict_extract(key, d):
                        yield result

def add_elements_to_item(item_key, dictionary, elements):
    print(f"Adding the following '{item_key}' to the cloud compose definition: {elements}")
    results = dict_extract(item_key, dictionary)
    for result in results:
        for key, value in elements.items():
            new_value = copy.deepcopy(value)
            if type(result[item_key]) == list:
                result[item_key].append({'Key': key, 'Value': new_value})
            elif type(result[item_key]) == dict:
                result[item_key][key] = new_value
            else:
                raise ValueError("type must be list or dict")

def update_keys(dictionary, new_keys):
    print(f"Making the following updates to the cloud compose definition: {new_keys}")
    for key, value in new_keys.items():
        results = dict_extract(key, dictionary)
        for result in results:
            new_value = copy.deepcopy(value)
            result[key] = new_value

def delete_keys(dictionary, keys):
    print(f"Deleting the following elements fromthe cloud compose definition: {keys}")
    for key in keys:
        results = dict_extract(key, dictionary)
        while results:
            result = next(results, None)
            if result:
                del result[key]
                results = dict_extract(key, dictionary)
            else:
                results = None

def extract_tag(tag_key, dictionary):
    results = dict_extract("Tags", dictionary)
    for result in results:
        for tag in result["Tags"]:
            if tag["Key"] == tag_key:
                return tag["Value"]

def unique_values(key, dictionary):
    values = set()
    for k, v in dictionary.items():
        if isinstance(v, dict):
            values.update(unique_values(key, v))
        elif k == key:
            values.add(v)
    return values

def ssl_certificate_arn(service_name, aws_hosted_zone):
    client_acm = boto3.client('acm')
    response = client_acm.request_certificate(
        DomainName=f'{service_name}.{aws_hosted_zone}',
        ValidationMethod='DNS',
    )
    return response['CertificateArn']

def stack_description(stack_name):
    client_cf = boto3.client('cloudformation')
    response = client_cf.list_stack_resources(
        StackName=stack_name,
    )
    return response

def logical_to_physical_id(description="", suffix=""):
    if not description or not suffix:
        print(
            "ERROR: function requires both a description and a logical "
            "id suffix")
    summary_list = description["StackResourceSummaries"]
    results = []
    len_suffix = len(suffix)
    for resource in summary_list:
        if resource["LogicalResourceId"][-len_suffix:] == suffix:
            results.append(resource["PhysicalResourceId"])
    return results

def validate_caa(hosted_zone, dns_service):
    result = pydig.query(hosted_zone,'CAA')
    success = False
    for item in result:
        if dns_service in item:
            success = True
    return success
