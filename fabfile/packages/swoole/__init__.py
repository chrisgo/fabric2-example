import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Swoole
https://www.swoole.co.uk/
"""

def install(c):
    util.start()
    # Install supervisor


    # Install Swoole PECL extension
    # https://www.swoole.co.uk/docs/get-started/installation
    if not exists('/usr/lib/php/20180731/swoole.so'):
        print('Installing Swoole Extension ...')
        c.sudo('echo "" | pecl install swoole')
        c.sudo('bash -c "echo extension=/usr/lib/php/20180731/swoole.so > /etc/php/7.3/mods-available/swoole.ini"')
        c.sudo('ln -s /etc/php/7.3/mods-available/swoole.ini /etc/php/7.3/fpm/conf.d/30-swoole.ini')
        c.sudo('ln -s /etc/php/7.3/mods-available/swoole.ini /etc/php/7.3/cli/conf.d/30-swoole.ini')
    util.done()

def configure(c):
    util.start()
    # Swoole
    util.done()
