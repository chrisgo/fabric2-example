import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Docker
https://docs.docker.com/engine/install/debian/
"""

def install(c):
    """
    Installs using docker
    """
    util.start()
    c.sudo('apt-get update')
    # Uninstall old docker
    print('Uninstall old versions of docker that might be around')
    c.sudo('apt-get remove docker docker-engine docker.io containerd runc')
    # Install basic packages
    print('Installing docker required packages')
    c.sudo('apt-get install -yq apt-transport-https ca-certificates curl gnupg-agent software-properties-common')
    # Add apt-key
    print('Installing docker ...')
    c.run('curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -')
    # Add apt-repositor
    c.sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"')
    # sudo apt-get update
    c.sudo('apt-get update')
    c.sudo('apt-get install docker-ce docker-ce-cli containerd.io')
    # Also install docker-compose
    # https://docs.docker.com/compose/install/
    print('Installing docker-compose ...')
    c.sudo('curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose')
    c.sudo('chmod +x /usr/local/bin/docker-compose')
    util.done()


def configure(c):
    util.start()
    util.done()
