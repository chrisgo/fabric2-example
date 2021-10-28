import pprint
import importlib
import os
import sys
from invoke import Collection
from fabric import Config
from fabric import task

__all__ = [
    'cron',
    'database',
    'node',
    'proxy',
    'puppet',
    'redis',
    'search',
    'socket',
    'worker',
    'www',
]
