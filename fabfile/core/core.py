import pprint
import importlib
import os
import sys
import inspect
import datetime
import json
import ast
from fabric import Config
from ..core import util
from fabfile.core.connection import Connection
from fabfile.roles import *
from fabfile.providers import *
from fabfile.packages import *

def normalize(config):
    """
    Main normalize() function
    """
    # (1) Output task start
    util.task_start(config.hosts)
    # (2) Start list of hosts we were able to run all the way through
    hosts = []
    # (3) Loop through the hostnames for this environment
    for host in config.hosts:
        # (4) Display hostname
        util.task_host(host)
        # (5) Make sure we have the specific provider in the providers.* package
        if not f'providers.{config.provider}':
            raise Exit(f'Provider: {config.provider} not found')
        # (6) Create the main "connection object"
        c = Connection(host=host, user="root", connect_kwargs=config.connect_kwargs)
        # (7) If provider is vagrant, we need to set the user to 'vagrant' instead of root
        if config.provider == 'vagrant':
            print(f'Vagrant Host: {host} | Username: vagrant | Password: vagrant')
            c = Connection(host=host, user='vagrant', connect_kwargs={'password': 'vagrant'})
        # (8) Stuff the config object into the connection object
        c.config = config;
        # (9) Get the provider object
        provider = getattr(sys.modules[__name__], config.provider)
        # (10) Execute normalize function
        provider.normalize(c)
        # (11) Add to hosts
        hosts.append(host)
    # (12) Output task start
    util.task_end(hosts)


def server(config):
    """
    Main server() function
    """
    # (1) Output task start
    util.task_start(config.hosts)
    # (2) Start list of hosts we were able to run all the way through
    hosts = []
    # (3) Loop through the hostnames for this environment
    for host in config.hosts:
        # (4) Display hostname
        util.task_host(host)
        # (5) Make sure we have the specific provider in the providers.* package
        if not f'roles.{config.role}':
            raise Exit(f'Role: {config.role} not found')
        # (6) Create the main "connection object"
        c = Connection(host=host, user=config.project.username, connect_kwargs=config.connect_kwargs)
        # (7) If provider is vagrant, we need to set the user to 'vagrant' instead of root
        if config.provider == 'vagrant':
            print(f'Vagrant Host: {host} | Username: vagrant | Password: vagrant')
            c = Connection(host=host, user='vagrant', connect_kwargs={'password': 'vagrant'})
        # (8) Stuff the config object into the connection object
        c.config = config;
        # (9) Add SSH Keys
        base.add_keys(c)
        # (10) Install base packages
        base.install(c)
        base.configure(c)
        # (11) Install firewall
        ufw.install(c)
        ufw.configure(c)
        # (12) Install certbot
        certbot.install(c)
        certbot.configure(c)
        # (13) Get the role object
        role = getattr(sys.modules[__name__], config.role)
        # (14) Execute normalize function
        role.server(c)
        # (15) Add to hosts
        hosts.append(host)
    # (12) Output task start
    util.task_end(hosts)


def project(config):
    """
    Main project() function
    """
    # (1) Output task start
    util.task_start(config.hosts)
    # (2) Start list of hosts we were able to run all the way through
    hosts = []
    # (3) Loop through the hostnames for this environment
    for host in config.hosts:
        # (4) Display hostname
        util.task_host(host)
        # (5) Make sure we have the specific provider in the providers.* package
        if not f'roles.{config.role}':
            raise Exit(f'Role: {config.role} not found')
        # (6) Create the main "connection object"
        c = Connection(host=host, user=config.project.username, connect_kwargs=config.connect_kwargs)
        # (7) If provider is vagrant, we need to set the user to 'vagrant' instead of root
        if config.provider == 'vagrant':
            print(f'Vagrant Host: {host} | Username: vagrant | Password: vagrant')
            c = Connection(host=host, user='vagrant', connect_kwargs={'password': 'vagrant'})
        # (8) Stuff the config object into the connection object
        c.config = config;
        # (9) Get the role object
        role = getattr(sys.modules[__name__], config.role)
        # (10) Execute normalize function
        role.project(c)
        # (11) Add to hosts
        hosts.append(host)
    # (12) Output task start
    util.task_end(hosts)


def release(config):
    """
    TODO: Move the main release() function here
    """
    # (1) Output task start
    util.task_start(config.hosts)
    # (2) Start list of hosts we were able to run all the way through
    hosts = []
    # (3) Loop through the hostnames for this environment
    for host in config.hosts:
        # (4) Display hostname
        util.task_host(host)
        # (5) Make sure we have the specific provider in the providers.* package
        if not f'roles.{config.role}':
            raise Exit(f'Role: {config.role} not found')
        # (6) Create the main "connection object"
        c = Connection(host=host, user=config.project.username, connect_kwargs=config.connect_kwargs)
        # (7) If provider is vagrant, we need to set the user to 'vagrant' instead of root
        if config.provider == 'vagrant':
            print(f'Vagrant Host: {host} | Username: vagrant | Password: vagrant')
            c = Connection(host=host, user='vagrant', connect_kwargs={'password': 'vagrant'})
        # (8) Stuff the config object into the connection object
        c.config = config;
        # (9) Get the role object
        role = getattr(sys.modules[__name__], config.role)
        # (10) Execute normalize function
        role.release(c)
        # (11) Add to hosts
        hosts.append(host)
    # (12) Output task start
    util.task_end(hosts)


def renew_cert(config):
    """
    Renew SSL Cert
    """
    print('==================================================')
    print('Renew Letsencrypt SSL Cert (Common)')
    print('==================================================')
    # (1) Output task start
    util.task_start(config.hosts)
    # (2) Start list of hosts we were able to run all the way through
    hosts = []
    letsencrypt_dir = f'/etc/letsencrypt/live/{config.project.name}.com'
    # (3) Loop through the hostnames for this environment
    for host in config.hosts:
        # (4) Display hostname
        util.task_host(host)
        # (5) See if we are running certbot or just copying files around
        if host == config.certbot.host:
            print('Renewing SSL Cert ...')
            # (6) Make sure we have the specific role in the roles.* package
            #if not hasattr(roles, config.role):
            #    raise c.exit(host, f'Role: {config.role} not found')
            # (7) Create the main "connection object"
            c = Connection(host=host, user=config.project.username, connect_kwargs=config.connect_kwargs)
            if config.provider == 'vagrant':
                print(f'Vagrant Host: {host} | Username: vagrant | Password: vagrant')
                c = Connection(host=host, user='vagrant', connect_kwargs={'password': 'vagrant'})
            c.config = config;
            # (8) Run the role
            c.sudo('certbot renew')
            c.get(f'{letsencrypt_dir}/privkey.pem', 'fabfile/environments/ssl/privkey.pem')
            c.get(f'{letsencrypt_dir}/fullchain.pem', 'fabfile/environments/ssl/fullchain.pem')
            print(Fore.YELLOW + 'Renewing SSL Cert ...' + Style.RESET_ALL)
            # (9) Add to hosts
            hosts.append(host)
        else:
            print('NO')
            print(f'Copying SSL Cert to {host}')
            #local('openssl x509 -dates -noout < fabfile/environments/ssl/fullchain.pem')
            if not c.exists(letsencrypt_dir):
                c.sudo(f'mkdir -p {letsencrypt_dir}')
            c.sudo_put('fabfile/environments/ssl/privkey.pem', '%s/privkey.pem' % letsencrypt_dir)
            c.sudo_put('fabfile/environments/ssl/fullchain.pem', '%s/fullchain.pem' % letsencrypt_dir)
            c.sudo('/etc/init.d/nginx restart')
    # (9) Output task start
    util.task_end(hosts)
