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
Set up Linode to a normalized state to run base server setup

Linode creates the root user and allows you to specify the root
password during the creation of the virtual machine.  For our
purposes, the root password should be setup to

    env.linode_password

What we need from the Linode console:

    (1) ROOT password (you typed this in)
    (2) IP Address (Update DNS in roledefs to this IP)
"""

def normalize(c):
    """
    Normalize the Linode system/provider
    """
    print('==================================================')
    print('Linode')
    print('==================================================')
    print('Setting env.user to root (for now)')
    env.user = 'root'
    env.password = env.linode_password
    # Set the debian apt-get non-interactive shell
    c.run('export DEBIAN_FRONTEND=noninteractive')
    # Do update and upgrade for latest security patches
    c.run('apt-get update')
    c.run('apt-get upgrade --show-upgraded --yes')
    # Create standard user (chris)
    print(f'Setting up non-root standard user ({c.config.project.username}) ...')
    if not c.exists(f'/home/{c.config.project.username}'):
        c.run(f'useradd -m {c.config.project.username}')
        c.run(f'echo "{c.config.project.username}:{c.config.project.password}"|chpasswd')
        if not c.exists('/home/{c.config.project.username}/.ssh/id_rsa.pub'):
            c.sudo('ssh-keygen -t rsa', user=env.base_user, pty=False)
    else:
        print(f'User found: {c.config.project.username}')
    # Install and configure sudo
    print('Setting up sudo ...')
    c.run('apt-get install sudo')
    if not c.exists('/etc/sudoers.orig'):
        c.run('cp /etc/sudoers /etc/sudoers.orig')
        #run('chmod 0640 /etc/sudoers.orig')
    c.run(f'echo "{c.config.project.username}   ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers')
    # Setup static IP
    print('Setting up static IP ...')
    # Get the IP address
    # http://www.if-not-true-then-false.com/2010/linux-get-ip-address/
    ip = c.run('/sbin/ifconfig eth0 | grep "inet addr" | awk -F: \'{print $2}\' | awk \'{print $1}\'')
    # Use static IP to guess the gateway (xxx.xxx.xxx.1)
    gateway = '%s.%s.%s.1' % (ip.split('.')[0], ip.split('.')[1], ip.split('.')[2])
    # http://library.linode.com/networking/configuring-static-ip-interfaces
    # Set the hostname
    #run('echo "%s" > /etc/hostname' % env.host_string.split('.')[0])
    #run('hostname -F /etc/hostname')
    # /etc/hosts file
    #if not exists('/etc/hosts.orig'):
    #   sudo('cp /etc/hosts /etc/hosts.orig')
    #cmd = 'echo -e "%s \t %s \t %s" >> /etc/hosts' % (ip, env.host_string, env.host_string.split('.')[0])
    #run(cmd)
    # Disable root ssh access (do this at the end)
    print('Disable ssh for root user ...')
    # This basically kicks you out as root and need to login as somebody else
    #sed('/etc/ssh/sshd_config', 'PermitRootLogin yes', 'PermitRootLogin no', use_sudo=True, backup='.bak', flags='')
    #run('/etc/init.d/ssh restart')
    print(f'Setting env.user back to {c.config.project.username}')
    env.user = env.base_user
    print('==================================================')
    print('... done Linode')
    print('==================================================')
