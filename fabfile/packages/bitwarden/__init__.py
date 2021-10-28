import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Bitwarden
https://bitwarden.com/
Password server
"""

def install(c):
    """
    Installs using docker
    """
    util.start()
    c.run("curl -Lso bitwarden.sh https://go.btwrdn.co/bw-sh && chmod +x bitwarden.sh")
    c.sudo("./bitwarden.sh install")
    c.sudo("../bitwarden.sh start")
    util.done()


def configure(c):
    util.start()
    util.done()
