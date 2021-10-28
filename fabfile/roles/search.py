import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.packages import *

"""
Search (Elasticsearch) Build and Setup
"""

def server(c):
    """
    Setup search for "search" role
    """
    print('==================================================')
    print('Building Search (Elasticsearch)')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Set the user
    #env.user = env.base_user
    #env.password = env.base_password
    # Run apt update
    c.sudo('apt-get update')
    # Install SOLR
    #elasticsearch.install()
    #elasticsearch.configure()
    # Papertrail
    if (util.enabled(c.config, 'papertrail')):
        papertrail.install(c)
        papertrail.configure(c)
    # S3FS
    if (util.enabled(c.config, 's3fs')):
        s3fs.install(c)
        s3fs.configure(c)

    print('==================================================')
    print('... done Building Search (Elasticsearch)')
    print('==================================================')


def project(c):
    """
    Project Setup
    """
    print('==================================================')
    print('Setup/Install Project on Search (Elasticsearch)')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Run update
    print('==================================================')
    print('... done Setup/Install Project on Search (Elasticsearch)')
    print('==================================================')
