import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.packages import *

"""
Proxy Server
For accessing Mercury Network websites.  For some reason
our IP is getting blocked, we have tried VPN, etc.
"""

def server(c):
    """
    Setup "proxy" role
    """
    print('==================================================')
    print('Building Proxy Server')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Run apt update
    c.sudo('apt-get update')
    c.sudo('apt-get upgrade')
    squid.install(c)
    squid.configure(c)
    print('==================================================')
    print('... done Building Proxy Server')
    print('==================================================')


def project(c):
    """
    """
    print('==================================================')
    print('Setup/Install Project on Proxy Server')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Run update
    print('==================================================')
    print('... done Setup/Install Project on Proxy Server')
    print('==================================================')
