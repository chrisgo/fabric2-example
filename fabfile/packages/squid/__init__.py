import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Squid Proxy
http://www.squid-cache.org/

https://www.linode.com/docs/networking/squid/squid-http-proxy-ubuntu-12-04
"""

def install(c):
    util.start()
    c.sudo('apt-get install -yq squid3')
    util.done()

"""
Configure
"""
def configure(c):
    util.start()
    # Make a backup if the original is not there
    if not c.exists('/etc/squid3/squid.conf.orig'):
        c.sudo('mv /etc/squid3/squid.conf /etc/squid3/squid.conf.orig')
    # Move the original squid configuration over
    if c.exists('/etc/squid3/squid.conf'):
        c.sudo('rm /etc/squid3/squid.conf')
    # Copy our shortened version of the squid.conf over
    c.put_template('etc-squid3-squid.conf', '/etc/squid3/squid.conf', sudo=True)
    # Copy our special configuration over to server
    if c.exists('/etc/squid3/custom.conf'):
        c.sudo('rm /etc/squid3/custom.conf')
    c.put_template('etc-squid3-custom.conf', '/etc/squid3/custom.conf', sudo=True)
    # Restart to pick up new config
    c.sudo('/etc/init.d/squid3 restart')
    # Enable the squid port on firewal
    c.sudo('ufw allow 3128')  # squid
    # re-enable firewall and print rules
    c.sudo('ufw --force enable')
    util.done()
