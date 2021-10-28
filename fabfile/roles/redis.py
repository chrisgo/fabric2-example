import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.packages import *

"""
Redis (+Resque) Server Build and Setup

Source: http://etagwerker.wordpress.com/2011/06/27/how-to-setup-resque-web-with-nginx-and-unicorn/
"""

def server(c):
    """
    Setup Redis (+Resque) Server with basic software for "redis" role
    """
    print('==================================================')
    print('Building Redis (+Resque) Server')
    print('==================================================')
    #c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Run apt update
    c.sudo('apt-get update')
    # Nginx
    nginx.install(c)
    nginx.configure(c)
    # Redis
    redis_server.install(c)
    redis_server.configure(c)
    # Resque
    resque_server.install(c)
    resque_server.configure(c)
    # Papertrail
    if (util.enabled(c.config, 'papertrail')):
        papertrail.install(c)
        papertrail.configure(c)
    # S3FS
    if (util.enabled(c.config, 's3fs')):
        s3fs.install(c)
        s3fs.configure(c)
    print('==================================================')
    print('... done Building Redis (+Resque) Server')
    print('==================================================')


def project(c):
    """
    Installs and setup Redis (+Resque) server with project specifics
    """
    print('==================================================')
    print('Setup/Install Project on Redis (+Resque) Server')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Set up queues

    print('==================================================')
    print('... done Setup/Install Project on Redis (+Resque) Server')
    print('==================================================')
