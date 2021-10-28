import pprint
import importlib
import os
import sys
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task

__all__ = [
    'aws',
    'digitalocean',
    'linode',
    'vagrant',
]
