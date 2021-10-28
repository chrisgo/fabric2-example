import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.packages import *

"""
Puppeteer

The node server serves a couple of things for our technology stack

(1) Encompass Automation: using Puppeteer
(2) TODO: Web Scraping:   using Puppeteer

"""

def server(c):
    """
    Setup Nodejs with basic software for "node" role
    """
    print('==================================================')
    print('Building Puppet Server')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Run apt update
    c.sudo('apt-get update')
    # Install node
    nodejs.install(c)
    nodejs.configure(c)
    # Install xvfb
    puppeteer.install(c)
    puppeteer.configure(c)
    # Papertrail
    #if (util.enabled(c.config, 'papertrail'):
    #    papertrail.install()
    #    papertrail.configure()
    # S3FS
    #if (util.enabled(c.config, 's3fs'):
    #    s3fs.install()
    #    s3fs.configure()
    print('==================================================')
    print('... done Building Puppet Server')
    print('==================================================')


@task
def project(c):
    print('')
    print(f'Use the fabric script in the {c.config.project.name}/puppeteer project')
    print('... the project_setup() is defined there')
    print('')

@task
def release(c, branch=''):
    print('')
    print(f'Use the fabric script in the {c.config.project.name}/puppeteer project')
    print('... the release() is defined there')
    print('')
