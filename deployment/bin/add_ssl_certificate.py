#!/usr/bin/env python3

# code inspired by:
# https://stackoverflow.com/questions/68952765/unable-to-attach-acm-public-certificate-with-alb-listener-using-lambda-across-ac

import sys
import os
import pprint
import time

import boto3

from common import stack_description, logical_to_physical_id, \
    ssl_certificate_arn, validate_caa

try:
    debug = (os.environ["DEBUG"] == "true")
    service_name = os.environ["SERVICE_NAME"]
    aws_region = os.environ["AWS_REGION"]
    aws_hosted_zone = os.environ["AWS_HOSTED_ZONE"]
    stack_name = os.environ["STACK_NAME"]
    aws_hosted_zone_id = os.environ["AWS_HOSTED_ZONE_ID"]

except KeyError as err:
    print("ERROR: missing environment variable!")
    print(err)
    sys.exit()

my_description = stack_description(stack_name)
listener_arn = logical_to_physical_id(my_description, "Listener")[0]
target_group_arn = logical_to_physical_id(my_description, "TargetGroup")[0]
load_balancer_arn = logical_to_physical_id(my_description, "LoadBalancer")[0]

client_elb = boto3.client('elbv2')
client_acm = boto3.client('acm')
client_route53 = boto3.client('route53')

ca_authority = "amazon.com"
if validate_caa(aws_hosted_zone, ca_authority):
    print(f"{ca_authority} is a valid certificate authority for {aws_hosted_zone}.")
else:
    print(f"ERROR: {ca_authority} is NOT a valid certificate authority "
          f"for {aws_hosted_zone}.")
    print(f"Please update the DNS records for {aws_hosted_zone}")
    print(f"For more information: https://aws.amazon.com/premiumsupport/knowledge-center/acm-troubleshoot-caa-errors/")
    sys.exit()

# get certificate
certificate_arn = ssl_certificate_arn(f"{service_name}6", aws_hosted_zone)
print(f'certificate_arn: {certificate_arn}')

acm_describe = client_acm.describe_certificate(
    CertificateArn=certificate_arn
)
if debug:
    print("Certificate description:")
    pprint.pprint(acm_describe)

if acm_describe['Certificate']['Status'] == 'ISSUED':
    print("Certificate has been successfully issued.")
    sys.exit()

print("Sleeping for 10 seconds...")
time.sleep(10)
acm_describe = client_acm.describe_certificate(
    CertificateArn=certificate_arn
)

try:
    name = acm_describe['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Name']
    value = acm_describe['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Value']
except KeyError as ex:
    print(ex)
    print(f"ERROR: no valid validation options for certificate {certificate_arn}.")
    print("Please try again.")
    sys.exit()

#validating acm certificate using DNS
record_type = "CNAME"

acm_validation = client_route53.test_dns_answer(
    HostedZoneId=aws_hosted_zone_id,
    RecordName=name,
    RecordType=record_type,
)

if ('RecordName' in acm_validation
    and 'RecordData' in acm_validation
    and acm_validation["RecordName"] == name):
        print("DNS record already created correctly.")
else:
    print ("Creating new DNS record.")
    acm_validation = client_route53.change_resource_record_sets(
        HostedZoneId=aws_hosted_zone_id,
        ChangeBatch={
            'Comment': 'DNS Validation',
            'Changes': [
                {
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': record_type,
                        'TTL': 1800,
                        'ResourceRecords': [
                            {
                                'Value': value
                            },
                        ],
                    }
                },
            ]
        }
    )
    print("Sleeping for 10 seconds...")
    time.sleep(10)

    acm_validation = client_route53.test_dns_answer(
        HostedZoneId=aws_hosted_zone_id,
        RecordName=name,
        RecordType=record_type,
    )
    if ('RecordName' in acm_validation
        and 'RecordData' in acm_validation
        and acm_validation["RecordName"] == name):
            print ("DNS record was created correctly.")
    else:
        print("WARNING: DNS record not created correctly. Please try again.")
        sys.exit()

print("Waiting for acm to get validated using dns.")
print("Note: It might take several hours for Amazon to validate this.")
if debug:
    print(f"For more information: https://aws.amazon.com/blogs/security/easier-certificate-validation-using-dns-with-aws-certificate-manager/#:~:text=The%20certificate%20you%20requested%20is,it%20and%20issue%20the%20certificate.")

waiter = client_acm.get_waiter('certificate_validated')
waiter.wait(
    CertificateArn=certificate_arn,
    WaiterConfig={
        'Delay': 15,
        'MaxAttempts': 80
    }
)

print("Sleeping for 10 seconds...")
time.sleep(10)

acm_describe = client_acm.describe_certificate(
    CertificateArn=certificate_arn
)
# pprint.pprint(acm_describe)

sys.exit()

print("creating listener")
response = client_elb.create_listener(
    LoadBalancerArn=load_balancer_arn,
    Protocol='HTTPS',
    Port=443,
    Certificates=[
        {
            'CertificateArn': certificate_arn,
        },
    ],
    DefaultActions=[{
        'Type': 'forward',
        'TargetGroupArn': target_group_arn,
    }]
)
print(response)
# client_elb.modify_listener(
#     ListenerArn=listener_arn,
#     Certificates=[
#         {
#             'CertificateArn': certificate_arn,
#         },
#     ],
# )
# response = client.modify_listener(
#     ListenerArn='string',
#     Port=123,
#     Protocol='HTTP'|'HTTPS'|'TCP'|'TLS'|'UDP'|'TCP_UDP'|'GENEVE',
#     SslPolicy='string',
#     Certificates=[
#         {
#             'CertificateArn': 'string',
#             'IsDefault': True|False
#         },
#     ],
#     DefaultActions=[
#         {
#             'Type': 'forward'|'authenticate-oidc'|'authenticate-cognito'|'redirect'|'fixed-response',
#             'TargetGroupArn': 'string',
#             'AuthenticateOidcConfig': {
#                 'Issuer': 'string',
#                 'AuthorizationEndpoint': 'string',
#                 'TokenEndpoint': 'string',
#                 'UserInfoEndpoint': 'string',
#                 'ClientId': 'string',
#                 'ClientSecret': 'string',
#                 'SessionCookieName': 'string',
#                 'Scope': 'string',
#                 'SessionTimeout': 123,
#                 'AuthenticationRequestExtraParams': {
#                     'string': 'string'
#                 },
#                 'OnUnauthenticatedRequest': 'deny'|'allow'|'authenticate',
#                 'UseExistingClientSecret': True|False
#             },
#             'AuthenticateCognitoConfig': {
#                 'UserPoolArn': 'string',
#                 'UserPoolClientId': 'string',
#                 'UserPoolDomain': 'string',
#                 'SessionCookieName': 'string',
#                 'Scope': 'string',
#                 'SessionTimeout': 123,
#                 'AuthenticationRequestExtraParams': {
#                     'string': 'string'
#                 },
#                 'OnUnauthenticatedRequest': 'deny'|'allow'|'authenticate'
#             },
#             'Order': 123,
#             'RedirectConfig': {
#                 'Protocol': 'string',
#                 'Port': 'string',
#                 'Host': 'string',
#                 'Path': 'string',
#                 'Query': 'string',
#                 'StatusCode': 'HTTP_301'|'HTTP_302'
#             },
#             'FixedResponseConfig': {
#                 'MessageBody': 'string',
#                 'StatusCode': 'string',
#                 'ContentType': 'string'
#             },
#             'ForwardConfig': {
#                 'TargetGroups': [
#                     {
#                         'TargetGroupArn': 'string',
#                         'Weight': 123
#                     },
#                 ],
#                 'TargetGroupStickinessConfig': {
#                     'Enabled': True|False,
#                     'DurationSeconds': 123
#                 }
#             }
#         },
#     ],
#     AlpnPolicy=[
#         'string',
#     ]
# )


# CAA Error:
# {'Certificate': {'CertificateArn': 'arn:aws:acm:us-west-2:714774317425:certificate/007ff7ab-e95c-4ef8-a73e-0a874e13c2e2',
#                  'CreatedAt': datetime.datetime(2023, 1, 19, 13, 44, 30, 581000, tzinfo=tzlocal()),
#                  'DomainName': 'yelb4.democracygps.org',
#                  'DomainValidationOptions': [{'DomainName': 'yelb4.democracygps.org',
#                                               'ValidationDomain': 'yelb4.democracygps.org',
#                                               'ValidationMethod': 'DNS',
#                                               'ValidationStatus': 'FAILED'}],
#                  'ExtendedKeyUsages': [],
#                  'FailureReason': 'CAA_ERROR',
#                  'InUseBy': [],
#                  'Issuer': 'Amazon',
#                  'KeyAlgorithm': 'RSA-2048',
#                  'KeyUsages': [],
#                  'Options': {'CertificateTransparencyLoggingPreference': 'ENABLED'},
#                  'RenewalEligibility': 'INELIGIBLE',
#                  'SignatureAlgorithm': 'SHA256WITHRSA',
#                  'Status': 'FAILED',
#                  'Subject': 'CN=yelb4.democracygps.org',
#                  'SubjectAlternativeNames': ['yelb4.democracygps.org'],
#                  'Type': 'AMAZON_ISSUED'},
#  'ResponseMetadata': {'HTTPHeaders': {'content-length': '743',
#                                       'content-type': 'application/x-amz-json-1.1',
#                                       'date': 'Thu, 19 Jan 2023 22:02:03 GMT',
#                                       'x-amzn-requestid': 'aa3fc42b-d3ca-464d-a9b3-3e612f9cada3'},
#                       'HTTPStatusCode': 200,
#                       'RequestId': 'aa3fc42b-d3ca-464d-a9b3-3e612f9cada3',
#                     #   'RetryAttempts': 0}}