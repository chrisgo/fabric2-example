import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Install Grive2 which is a FUSE filesystem for google drive
https://github.com/vitalif/grive2
"""


def install(c):
    util.start()
    print("... Grive2 (https://github.com/vitalif/grive2)")
    c.sudo('apt-get install -yq git cmake build-essential')
    c.sudo('apt-get install -yq libgcrypt20-dev libyajl-dev')
    c.sudo('apt-get install -yq libboost-all-dev libcurl4-openssl-dev libexpat1-dev')
    c.sudo('apt-get install -yq libcppunit-dev binutils-dev')
    c.sudo('apt-get install -yq debhelper zlib1g-dev dpkg-dev pkg-config')
    if not c.exists(f'/home/{c.config.project.username}/gdrive'):
        c.run(f'mkdir /home/{c.config.project.username}/gdrive')
    if not c.exists(f'/home/{c.config.project.username}/projects'):
        c.run(f'mkdir /home/{c.config.project.username}/projects')
    c.run_with_cd(f'/home/{c.config.project.username}/projects', 'git clone https://github.com/vitalif/grive2.git')
    # Not really working
    c.run(f'/home/{c.config.project.username}/projects/grive2', 'dpkg-buildpackage -j4 --no-sign')
    util.done()


"""
Configure
"""
def configure(c):
    util.start()
    util.done()
