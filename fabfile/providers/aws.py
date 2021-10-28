import pprint
import importlib
import os
import sys
#from fabric import Connection
from invoke import Collection
from patchwork import files
from fabric import Config
from fabric import task
from fabfile.core import *

"""
Set up Amazon EC2 to a normalized state to run base server setup

EC2 requires you to login using a private key (.pem) file that you
create on the Amazon EC2 web console and then download to your local
system and use as a private key when connecting
"""

def normalize(c):
    """
    Normalize the Amazon EC2 system/provider
    """
    print('==================================================')
    print('Amazon EC2')
    print('==================================================')



    print('==================================================')
    print('... done Amazon EC2')
    print('==================================================')
    # Then run base server setup
    #execute('servers.base_server')


def add_ip(c, name, ip, type = 'A'):
    """
    Add IP to DNS load balancer
    """
    util.start()
    # client = boto3.resource('route53')
    # Create A record
    """
    response = client.create_traffic_policy(
        Name=name,
        Document='string',
        Comment='string'
    )
    """
    # Create Health Check
    """
    response = client.create_health_check(
        CallerReference='string',
        HealthCheckConfig={
            'IPAddress': 'string',
            'Port': 123,
            'Type': 'HTTP'|'HTTPS'|'HTTP_STR_MATCH'|'HTTPS_STR_MATCH'|'TCP'|'CALCULATED'|'CLOUDWATCH_METRIC',
            'ResourcePath': 'string',
            'FullyQualifiedDomainName': 'string',
            'SearchString': 'string',
            'RequestInterval': 123,
            'FailureThreshold': 123,
            'MeasureLatency': True|False,
            'Inverted': True|False,
            'HealthThreshold': 123,
            'ChildHealthChecks': [
                'string',
            ],
            'EnableSNI': True|False,
            'Regions': [
                'us-east-1'|'us-west-1'|'us-west-2'|'eu-west-1'|'ap-southeast-1'|'ap-southeast-2'|'ap-northeast-1'|'sa-east-1',
            ],
            'AlarmIdentifier': {
                'Region': 'us-east-1'|'us-west-1'|'us-west-2'|'eu-central-1'|'eu-west-1'|'ap-southeast-1'|'ap-southeast-2'|'ap-northeast-1'|'ap-northeast-2'|'sa-east-1',
                'Name': 'string'
            },
            'InsufficientDataHealthStatus': 'Healthy'|'Unhealthy'|'LastKnownStatus'
        }
    )
    """
    util.done()
