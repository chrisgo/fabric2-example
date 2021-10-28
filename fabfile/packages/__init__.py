#from __future__ import with_statement
#from fabric.api import *
#from fabric.colors import blue, cyan, green, magenta, red, white, yellow
#from fabric.contrib.console import confirm
#from fabric.contrib.files import *
import paramiko
import os
import json
import datetime
import inspect
import time
import pprint
from invoke import Exit
from patchwork import files
from colorama import Fore, Back, Style
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task

__all__ = [
    'automysqlbackup',
    'base',
    'bitwarden',
    'centrifugo',
    'certbot',
    'docker',
    'elasticsearch',
    'filesystem',
    'gdrive',
    'git',
    'logdna',
    'mariadb',
    'meilisearch',
    'mysqltuner',
    'netdata',
    'newrelic',
    'nginx',
    'nodejs',
    'papertrail',
    'php',
    'php73',
    'php_resque',
    'pm2',
    'postgresql',
    'puppeteer',
    'python',
    #'python27',
    'redis_server',
    'resque_server',
    'rocketchat',
    #'s3fs',
    'selfsignedcert',
    'squid',
    'ssh',
    'supervisor',
    'swoole',
    'ufw',
]
