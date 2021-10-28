import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Supervisor for the worker

"""

def install(c):
    util.start()
    print("... Supervisor")
    # https://laravel.com/docs/5.7/queues#supervisor-configuration
    c.sudo('apt-get install -yq supervisor')
    util.done()

"""
Configure
"""
def configure(c):
    util.start()
    c.put_template('horizon.conf', '/etc/supervisor/conf.d/horizon.conf', sudo=True)
    c.sed('/etc/supervisor/conf.d/horizon.conf', '{{user}}', c.config.project.username, sudo=True)
    c.sudo('supervisorctl reread')
    c.sudo('supervisorctl update')
    c.sudo('supervisorctl start horizon:*')
    util.done()
