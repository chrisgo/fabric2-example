import pprint
import importlib
import os
import sys
#from fabric2 import Connection
from invoke import Collection
from patchwork import files
from fabric import Config
from fabric import task
from fabfile.core import *

"""
Set up Vagrant to a normalized state to run base server setup

Vagrant creates a default user vagrant/vagrant that has sudo powers.
We use this to create the base user and right now, we don't touch
the su user at all

To reset a vagrant box:

cd ~/Servers/Project (directory with Vagrantfile)
vagrant destroy
vagrant up
"""

def normalize(c):
    """
    Normalize the Vagrant system/provider
    """
    print('==================================================')
    print('Vagrant')
    print('==================================================')
    _username = c.config.project.username
    _password = c.config.project.password
    c.run('export DEBIAN_FRONTEND=noninteractive')
    # Set the root password to a known password (???)
    # Do update and upgrade for latest security patches
    c.sudo('apt-get update')
    c.sudo('apt-get -yq remove postfix')
    c.sudo('apt-get -y upgrade --show-upgraded --yes')
    # Install and configure sudo
    print('Setting up sudo ...')
    c.sudo_passthrough('cp /etc/sudoers /etc/sudoers.tmp')
    c.sudo('chmod 777 /etc/sudoers.tmp')
    c.sudo(f'echo "{_username}  ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.tmp')
    c.sudo('chmod 0440 /etc/sudoers.tmp')
    c.sudo('mv /etc/sudoers.tmp /etc/sudoers')
    # Create standard user (chris)
    print(f'Setting up non-root standard user ({_username}) ...')
    if not c.exists(f'/home/{_username}'):
        c.sudo(f'useradd -m {_username}')
        #c.sudo(f'echo "{_username}:{_password}"|chpasswd')
    else:
        print(f'User found: {_username}')
    # Setup static IP
    print('Setting up static IP ...')
    # Not sure if this is needed
    print('Disable ssh for root user ...')
    # This basically kicks you out as root and need to login as somebody else
    #sed('/etc/ssh/sshd_config', 'PermitRootLogin yes', 'PermitRootLogin no', use_sudo=True, backup='.bak', flags='')
    #sudo('/etc/init.d/ssh restart')
    # Set up the hostname
    c.sudo(f'hostnamectl set-hostname {c.host}')
    c.append('/etc/hosts', '# Added for hostname loopback', sudo=True)
    c.append('/etc/hosts', f'127.0.0.1   {c.host}', sudo=True)
