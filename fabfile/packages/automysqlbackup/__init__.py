import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
AutoMysqlBackup

*** CURRENTLY done by prd-mdb7.{_project_name}.com ***

2/7/21 CG: Automysqlbackup seems to be failing to write directly to S3
because it has to dump the database to SQL file, then zip it up
So the first write is about 50++ GB (raw/uncompressed)
Then it has to go and zip this up across the network 80 GB to 2 GB

For now, we are going to try to dump it to the local disk
/var/backups/automysqlbackup (then subfolders called daily, weekly, monthly)
Then we will use s3cmd sync to send it up to s3 after the process is done

sudo s3cmd --config /home/{_project_name}/.s3cfg sync -r /var/backups/automysqlbackup s3://s3fs.{_project_name}.com/database/

"""

def install(c):
    util.start()
    # Install automysqlbackup
    if not c.enabled('automysqlbackup'):
        util.done('Not enabled in environment settings')
        #sudo('/etc/init.d/automysqlbackup stop')
        return
    c.sudo('apt-get install -yq automysqlbackup')
    # Create the backup directory
    if not c.exists(c.config.automysqlbackup.dir):
        c.sudo(f'mkdir -p {c.config.automysqlbackup.dir}')
    util.done()

def configure(c):
    util.start()
    if not c.enabled('automysqlbackup'):
        util.done('Not enabled in environment settings')
        return
    # Configure
    if (env.automysqlbackup_dir and env.automysqlbackup_dir != ''):
        search = 'BACKUPDIR="/var/lib/automysqlbackup"'
        replace = f'BACKUPDIR="{c.config.automysqlbackup.dir}"'
        c.sed('/etc/default/automysqlbackup', search, replace, sudo=True)
        # 1/26/20 CG: To disable this, turn off the cron job
        # sudo vi /etc/cron.daily/automysqlbackup
        # comment all the lines in there
        # normally, we only want one server to be doing the backup
        # which could be the master or slave
    util.done()
