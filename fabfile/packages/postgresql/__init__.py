import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Installs Postgres Database
https://linuxhint.com/install_postgresql_debian10/
"""
def install(c):
    """
    Install postgres
    """
    util.start()
    c.sudo('apt-get update')
    print('Installing Postgresql')
    c.sudo('apt-get install -yq postgresql')
    # Restart if necessary
    c.sudo('/etc/init.d/postgresql restart')
    util.done()

"""
Configure
"""
def configure(c):
    util.start()
    print('Configuring Postgres ...')
    # Change password
    # c.sudo('passwd postgres')
    util.done()
