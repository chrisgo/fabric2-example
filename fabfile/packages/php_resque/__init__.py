import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
PHP Resque (using Minion)
"""

def install(c):
    util.start()
    util.done()

def configure(c):
    util.start()
    # Get the www_root
    www_root = c.config.project.www_root
    # Copy script over to /etc/init.d/php-resque
    c.put_template('php-minion-resque', '/etc/init.d/php-minion-resque', sudo=True)
    c.sudo('chmod +x /etc/init.d/php-minion-resque')
    c.sed('/etc/init.d/php-minion-resque', '{{www_root}}', f'{www_root}/..', sudo=True)
    c.sudo('/etc/init.d/php-minion-resque start')
    # Create another section for the scheduler worker
    c.put_template('php-minion-resque-scheduler', '/etc/init.d/php-minion-resque-scheduler', sudo=True)
    c.sudo('chmod +x /etc/init.d/php-minion-resque-scheduler')
    c.sed('/etc/init.d/php-minion-resque-scheduler', '{{www_root}}', f'{www_root}/..', sudo=True)
    c.sudo('/etc/init.d/php-minion-resque-scheduler start')
    util.done()
