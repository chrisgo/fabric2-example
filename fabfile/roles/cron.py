import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.packages import *

"""
Cron Build and Setup
"""

def server(c):
    """
    Setup cron/scheduler for "cron" role
    """
    print('==================================================')
    print('Building Cron Server')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Run apt update
    c.sudo('apt-get update')
    print('==================================================')
    print('... done Building Cron Server')
    print('==================================================')


def project(c):
    """
    """
    print('==================================================')
    print('Setup/Install Project on Cron Server')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Display note about not being able to programmatically add a crontab
    print('')
    print('')
    print('*******************************************************')
    print('***** We cannot automate the cronjob creation yet *****')
    print('*******************************************************')
    print('')
    print('For now, you have to ssh into the cron server')
    print(f'ssh {c.config.project.name}@{c.host}')
    print('')
    print('Then type:')
    print('crontab -e')
    print('')
    print('Add the following line:')
    print('* * * * * php /var/www/{{domain}}/php/minion Scheduler 1>> /dev/null 2>&1')
    print('')
    print('')
    #
    # Run update
    print('==================================================')
    print('... done Setup/Install Project on Cron Server')
    print('==================================================')
