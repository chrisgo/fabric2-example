import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Rocketchat
https://rocket.chat/

For now, we are just using the DigitalOcean Marketplace
1-click install process that pulls in Ubuntu 18.04
https://marketplace.digitalocean.com/apps/rocket-chat

We may have to do a "slower" install later so we can better control
the OS and all the other updates needed.  Currently, not being
used in PROD so not a big deal yet

"""

def install(c):
    """
    Install manually using
    https://docs.rocket.chat/installation/manual-installation/debian
    """
    util.start()
    util.done()


def configure(c):
    util.start()
    util.done()
