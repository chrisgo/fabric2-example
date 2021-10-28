import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Meilisearch
https://docs.meilisearch.com/create/how_to/running_production.html#step-2-run-meilisearch-as-a-service
"""

def install(c):
    util.start()
    util.done()


def configure(c):
    util.start()
    util.done()
