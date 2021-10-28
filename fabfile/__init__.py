import pprint
import importlib
import os
import sys
import inspect
import datetime
import json
import ast
from invoke import Collection
from invoke import Exit
#from invocations.console import confirm
from fabric import Config
from fabric import task
from colorama import Fore, Back, Style, Cursor
from .core import util
from .core import confirm
from .core.connection import Connection
from .core import core as _core
from fabfile.packages import git
from fabfile.core.fabtools import mysql as fabtools_mysql

"""

Fabric 2.x

fab dev www release
fab local --user=chris www release

  The old way of `fab2 local:chris www release` does not work anymore due
  to the new invoke framework
  http://docs.pyinvoke.org/en/latest/concepts/invoking-tasks.html#task-command-line-arguments

fab dev www normalize
fab dev www setup
fab dev www project

  Note: Task function names with underscore becomes a dash when typed in
  fab2 dev www server-normalize  <=>  server_normalize()
  http://docs.pyinvoke.org/en/stable/concepts/namespaces.html#dashes-vs-underscores

"""

# ==============================================================================
# (1) Load Configuration
#     Fabric2 does not have a global "env" object anymore so we have to create
#     it out here and this allows us to use it for all functions here
# ==============================================================================
# (1.1) Start a new config object that we can load up with other things
config = Config()
# (1.2) Load up the main configuration file
#config.loadme = 'LOADME_VAR_SO_WE_CAN_FIND_THIS'
#config.load_overrides({'sphinx': {'target': "docs/_build"}})
#config.load_overrides(environments.config)
base = importlib.import_module('fabfile.environments')
config.load_collection(base.config)

# ==============================================================================
# (2) Environments
#     The functions here just pull the correct config file to use in the
#     environments.* packages and does some rudimentary checks
# ==============================================================================

@task
def production(c):
    """
    ......... <environment> set up production environment
    """
    # (1) Get the name of environment
    config.environment = inspect.currentframe().f_code.co_name
    #print(f'***** {config.environment.upper()} (environments.{config.environment}) *****')
    # (2) Load up the config dictionary
    _config = importlib.import_module(f'fabfile.environments.{config.environment}')
    # (3) Stuff into config
    config.load_overrides(_config.config)
    confirm(config, sys.argv[2])


@task
def staging(c):
    """
    ......... <environment> set up staging environment
    """
    # (1) Get the name of environment
    config.environment = inspect.currentframe().f_code.co_name
    print(f'***** {config.environment.upper()} (environments.{config.environment}) *****')
    # (2) Load up the config dictionary
    _config = importlib.import_module(f'fabfile.environments.{config.environment}')
    # (3) Stuff into config
    config.load_overrides(_config.config)


@task
def dev(c):
    """
    ......... <environment> set up dev environment
    """
    # (1) Get the name of environment
    config.environment = inspect.currentframe().f_code.co_name
    print(f'***** {config.environment.upper()} (environments.{config.environment}) *****')
    # (2) Load up the config dictionary
    _config = importlib.import_module(f'fabfile.environments.{config.environment}')
    # (3) Stuff into config
    config.load_overrides(_config.config)


@task
def local(c, user='developer'):
    """
    ......... <environment> set up local (developer) environment
    """
    # (1) Get the name of environment with the "local_{user}" format
    environment_name = f'fabfile.environments.local_{user}'
    print(f'***** LOCAL (local_{user}) *****')
    # (2) Load up the config dictionary
    _config = importlib.import_module(environment_name)
    # (3) Stuff into config
    config.load_overrides(_config.config)


# ==============================================================================
# (3) Branches
#     3/13/21 CG: Not sure if these are still needed
# ==============================================================================

@task
def master(c):
    """
    ......... <branch> work on master branch
    """
    #env.branch = 'master'
    #env.roledefs = env.config.get('roledefs')
    #env.hosts = env.roledefs['www']


@task
def branch(c, branch_name):
    """
    ......... <branch> work on any specified branch
    """
    #env.branch = branch_name
    #env.roledefs = env.config.get('roledefs')
    #env.hosts = env.roledefs['www']


# ==============================================================================
# (4) Roles
#     The methods here mostly just pulls the list of hostnames (server namaes)
#     on the "role" we are running.  This uses the list of hostnames that are
#     set by the environment.* file that was pulled in one step earlier
# ==============================================================================

@task
def database(c):
    """
    ......... <role> database role
    """
    config.role = inspect.currentframe().f_code.co_name
    config.hosts = util.get_hosts_for_role(config, config.role)


@task
def redis(c):
    """
    ......... <role> redis role
    """
    config.role = inspect.currentframe().f_code.co_name
    config.hosts = util.get_hosts_for_role(config, config.role)


@task
def worker(c):
    """
    ......... <role> worker role
    """
    config.role = inspect.currentframe().f_code.co_name
    config.hosts = util.get_hosts_for_role(config, config.role)

@task
def www(c):
    """
    ......... <role> www (web+app) role
    """
    config.role = inspect.currentframe().f_code.co_name
    config.hosts = util.get_hosts_for_role(config, config.role)


# ==============================================================================
# (5) Main Commmands
#     The functions here does the bulk of the work once the config has been
#     pulled from environments.* and the list of hostnames has been set
#     Since each role could have a different set of things to do, we further
#     delegate any custom stuff to functions in roles.* using the name of the
#     the task as the role.taskname and execute the same function in there
# ==============================================================================

@task
def release(c):
    """
    Release code to an environment
    """
    _core.release(config)


@task
def normalize(c):
    """
    ..... (1) Initialize and normalize systems/providers
    """
    _core.normalize(config)


@task
def server(c):
    """
    ..... (2) Setup basic server software by role
    """
    _core.server(config)


@task
def project(c):
    """
    ..... (3) Setup project-specific installs by role
    """
    _core.project(config)


# ==============================================================================
# (6) Utility
# ==============================================================================

@task
def renew_cert(c):
    """
    Renew Letsencrypt SSL Cert (using certbot)
    """
    _core.renew_cert(config)


@task
def version(c):
    """
    Check server version
    """
    c.run(f'php /var/www/{c.config.project.name}/php/artisan System_Version')

# ==============================================================================
# (7) Test Tasks
# ==============================================================================

@task
def test(c):
    """
    ......... <role> <command> test
    """
    print('TEST')
    # (1) Output task start
    util.task_start(config.hosts)
    # (2) Start list of hosts we were able to run all the way through
    hosts = []
    # (3) Loop through the hostnames for this environment
    for host in config.hosts:
        print(host)
        # (4) Display hostname
        util.task_host(host)
        # (5) Create the main "connection object"
        c = Connection(host=host, user=config.project.username, connect_kwargs=config.connect_kwargs)
        c.config = config;
        #c.sudo('export DEBIAN_FRONTEND=noninteractive')
        # (6) Run any tests here
        #git.checkout(c)
        fabtools_mysql.test(c)
        # (7) Add to hosts
        hosts.append(host)
    # (9) Output task start
    util.task_end(hosts)
