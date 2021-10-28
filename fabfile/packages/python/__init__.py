import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Python
"""

def install(c):
    util.start()
    print('Installing Python, Pip and Virtualenv ...')
    c.sudo('apt-get update')
    c.sudo('apt-get install -yq python python-pip')
    c.sudo('pip install virtualenv')
    util.done()

def configure(c):
    util.start()
    util.done()
