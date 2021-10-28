import pprint
import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from .core.connection import Connection
from fabfile.core import *

"""
Universal Firewal (UFW) which is a wrapper around iptables
"""

def install(c):
    """
    Install UFW
    """
    util.start()
    c.sudo('apt-get install -yq ufw')
    util.done()

def configure(c):
    """
    Configure UFW
    """
    util.start()
    # http://guides.webbynode.com/articles/security/ubuntu-ufw.html
    # http://niteowebfabfile.readthedocs.org/en/latest/_modules/niteoweb/fabfile/server.html
    print("Enabling UFW (firewall)")
    # Change some things per here to eliminate errors
    # http://blog.kylemanna.com/linux/2013/04/26/ufw-vps/
    #sed('/etc/default/ufw', 'IPV6=yes', 'IPV6=no', use_sudo=True, backup='.bak', flags='')
    c.sed('/etc/default/ufw', 'IPT_MODULES=', '#IPT_MODULES=', sudo=True)
    # Reset
    c.sudo('ufw --force reset')
    # Apply rules
    c.sudo('ufw default deny')
    c.sudo('ufw allow 22')    # ssh
    c.sudo('ufw allow 53')    # rubygems
    c.sudo('ufw allow 80')    # web/http
    c.sudo('ufw allow 443')   # web/https
    c.sudo('ufw allow 3306')  # mysql
    c.sudo('ufw allow 5678')  # resque-web
    c.sudo('ufw allow 6379')  # redis
    # re-enable firewall and print rules
    c.sudo('ufw --force enable')
    c.sudo('ufw status verbose')
    util.done()
