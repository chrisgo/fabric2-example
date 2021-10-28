import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.core.fabtools import mysql as fabtools_mysql
from fabfile.packages import *

"""
Database Server Build and Setup
"""

def server(c):
    """
    Setup Database Server with basic software for "database" role
    """
    print('==================================================')
    print('Building Database Server')
    print('==================================================')
    c.run('export DEBIAN_FRONTEND=noninteractive')
    # Run apt update
    c.sudo('apt-get update')
    # Install nginx
    nginx.install(c)
    nginx.configure(c)
    # Install Mariadb (debian 11 bullseye installs mariadb 10.5)
    mariadb.install(c)
    mariadb.configure(c)
    # Papertrail
    if c.enabled('papertrail'):
        papertrail.install(c)
        papertrail.configure(c)
    # S3FS
    if c.enabled('s3fs'):
        s3fs.install(c)
        s3fs.configure(c)
    # Automysql backup
    if c.enabled('automysqlbackup'):
        automysqlbackup.install(c)
        automysqlbackup.configure(c)
    print('==================================================')
    print('... done Setup/Install Server on Database Server')
    print('==================================================')


def project(c):
    """
    Installs and setup Database server with project specifics
    """
    print('==================================================')
    print('Setup/Install Project on Database Server')
    print('==================================================')
    c.run('export DEBIAN_FRONTEND=noninteractive')
    #mount_root = env.config.get('mount_root', "/tmp")
    #aws_buckets = env.aws_buckets if ('aws_buckets' in env) else ""
    # (1) Create Database(s)
    # (1.1) Only create databases if we can find a list in the config
    if c.config.project.databases:
        _username = c.config.project.username
        _mysql = {
            'mysql_user': 'root',
            'mysql_password': c.config.project.password,
        }
        for database in c.config.project.databases:
            print(f'Checking database: {database}')
            if not fabtools_mysql.database_exists(c, database, **_mysql):
                # Create database and grant username@localhost
                fabtools_mysql.create_database(c, database, owner=_username, **_mysql)
                # Grant ALL username@'%'
                fabtools_mysql.grant_privileges(c, database, owner=_username, owner_host='%', **_mysql)
                # Readonly access for 'developer'@'%'
                fabtools_mysql.grant_privileges(c, database, owner='developer', owner_host='%', privileges='SELECT, SHOW VIEW', **_mysql)
                print(f'Database schema {database} created')
    # (2) Mount project folders (whatever is defined)
    print("Mounting project directories ...")
    # Mount S3
    if c.enabled('s3fs'):
        s3fs.mount(mount_root, aws_buckets)
    else:
        print("NOT mounting S3FS")
    util.done()
    print('==================================================')
    print('... done Setup/Install Project on Database Server')
    print('==================================================')


def master_setup(c):
    """
    Setup master
    """
    mariadb.configure_master(c)


def slave_setup(c):
    """
    Setup slave
    """
    mariadb.configure_slave(c)


def multimaster_setup(c):
    """
    Setup multi-master
    """
    print("---- Setting up multi-master database -----")
