import pprint
import importlib
import os
import sys
from invoke import Collection
from patchwork import files
from fabric import Config
from fabric import task
from fabfile.core import *

"""
Set up DigitalOcean to a normalized state to run base server setup

To reset a DigitalOcean droplet:

1) Login to http://digitalocean.com
2) Decide on name like dev-www.domain.com, staging-www.domain.com, etc.
3) Create a new Droplet using image: Debian 6.0 x64
4) Login to GoDaddy and create DNS entry to match name and IP address
5) DigitalOcean will email you the root password
6) SSH into new server (using IP) and change root password to

   env.password in environments/__init__.py

When doing a DESTROY to rebuild servers, sometimes the monitoring
agent goes into a weird state and fabric is unable to do a simple
sudo apt-get update

You have to do the following to get it back to normal
https://www.digitalocean.com/docs/monitoring/how-to/install-agent/

sudo apt-get install -yq gnupg
vi etc/apt/sources.list.d/digitalocean-agent.list
deb https://repos.insights.digitalocean.com/apt/do-agent/ main main
curl https://repos.insights.digitalocean.com/sonar-agent.asc | sudo apt-key add -

"""

def normalize(c):
    """
    Normalize the DigitalOcean system/provider
    """
    print('==================================================')
    print('DigitalOcean')
    print('==================================================')
    # (1) Set non-interactive
    c.run('export DEBIAN_FRONTEND=noninteractive')
    # (2) Update packages and upgrade for latest security patches
    c.run('apt-get update')
    c.run('apt-get upgrade --show-upgraded --yes')
    # (3) Create standard user
    _username = c.config.project.username
    _password = c.config.project.password
    print(f'Setting up non-root standard user {_username} ...')
    if not c.exists(f'/home/{_username}'):
        c.run(f'useradd -m {_username}')
        c.run(f'echo "{_username}:{_password}"|chpasswd')
    else:
        print(f'User found: {_username}')
    # (4) Install and configure sudo
    print('Setting up sudo ...')
    c.run('apt-get install sudo')
    if not c.exists('/etc/sudoers.orig'):
        c.run('cp /etc/sudoers /etc/sudoers.orig')
        #run('chmod 0640 /etc/sudoers.orig')
    c.run(f'echo "{_username}   ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers')
    # (5) Update the hostname of the server
    print(f'Setting server to hostname: {c.host}')
    c.run(f'echo "{c.host}" > /etc/hostname')
    c.run(f'hostnamectl set-hostname {c.host}')
    # (6) Disable root ssh access (do this at the end)
    #     8/31/18 CG: DO is now creating the /etc/hostname weird so we have to set it to the FQDN
    #     https://linuxize.com/post/how-to-change-hostname-on-debian-9/
    #     This basically kicks you out as root and need to login as somebody else
    print('Disable ssh for root user ...')
    print(f'Setting up non-root standard user {_username} ...')
    c.sed('/etc/ssh/sshd_config', 'PermitRootLogin yes', 'PermitRootLogin no', sudo=True)
    c.run('/etc/init.d/ssh restart')
    print('==================================================')
    print('... done DigitalOcean')
    print('==================================================')
