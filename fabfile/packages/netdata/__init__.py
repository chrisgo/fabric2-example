import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Netdata
"""

def install(c):
    util.start()
    c.sudo('apt-get update')
    c.run('bash <(curl -Ss https://my-netdata.io/kickstart.sh)')
    util.done()

def configure(c):
    util.start()
    print('Adding new virtual host')
    # Delete old virtual host file
    if c.exists('/etc/nginx/sites-available/netdata'):
        c.sudo('rm /etc/nginx/sites-available/netdata')
        print('Found old virtual host, archiving')
    # Link to sites-enabled
    if not c.exists('/etc/nginx/sites-enabled/netdata'):
        c.sudo_with_cd('/etc/nginx/sites-enabled', 'ln -s ../sites-available/netdata netdata')
    c.sudo('/etc/init.d/nginx restart')
    util.done()
