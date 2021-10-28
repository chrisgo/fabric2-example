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

#
# Utility functions
#

def sed_escape(string):
    """
    If we are passing slashes into sed (for example file paths: /tmp/test.txt)
    we need to escape those slashes '/' into '\/' to get it through
    TODO:
    3/20/21 CG: At some point, we want Connection.sed() to be able to this on
    it's own if it detects a '/' character to just escape it by itself
    """
    return string.replace('/', '\/')

def get_hosts_for_role(config, role):
    """
    Get the list of hosts for the server role
    """
    # (1) Make sure there is a "hostnames"
    if 'hostnames' not in config:
        raise Exit('No hostnames found in config')
    # (2) Make sure config.role in hostnames
    if role not in config.hostnames:
        raise Exit(f'No hostnames found for {role}')
    # (3) Get the final hostnames for the role
    return config.hostnames[role]


def task_start(hosts):
    """
    Prints Green START bar to screen
    """
    # (1) Get the function name
    function_name = ''
    stack = inspect.stack()
    function_name = stack[1][3]
    #title = f'Starting {module_name}.{function_name}()'
    #dashes = '-' * (49-len(title))
    #print(Fore.GREEN + f'{title} {dashes}' + Style.RESET_ALL)
    # (2) Line breaks
    print('\n\n')
    # (3) Green START Bar
    start = Back.GREEN + Style.BRIGHT + ' START ' + Style.RESET_ALL + ' running ' + \
            Style.BRIGHT + function_name + '()' + Style.RESET_ALL + \
            ' on ' + Back.WHITE + Fore.BLACK + ' ' + str(len(hosts)) + ' ' + Style.RESET_ALL + ' hosts'
    print(start)
    # (3) Loop through list of hostnames to output
    counter = 0
    for host in hosts:
        counter += 1
        print(Style.DIM + '        [' + str(counter) + '] ' + Style.RESET_ALL + host)


def task_end(hosts):
    """
    Prints Green END bar to screen
    """
    # (1) Get the function name
    function_name = ''
    stack = inspect.stack()
    function_name = stack[1][3]
    #title = f'Starting {module_name}.{function_name}()'
    #dashes = '-' * (49-len(title))
    #print(Fore.GREEN + f'{title} {dashes}' + Style.RESET_ALL)
    # (2) Line breaks
    print('\n')
    # (3) Green END Bar
    end = Back.GREEN + Style.BRIGHT + '  END  ' + Style.RESET_ALL + Fore.GREEN + ' success ' + Style.RESET_ALL + \
          Style.BRIGHT + function_name + '()' + Style.RESET_ALL + \
          ' on ' + Back.WHITE + Fore.BLACK + ' ' + str(len(hosts)) + ' ' + Style.RESET_ALL + ' hosts'
    print(end)
    # (4) Loop through list of hostnames to output
    counter = 0
    for host in hosts:
        counter += 1
        print(Fore.GREEN + '        [' + str(counter) + '] ' + Style.RESET_ALL + host)
    print('\n')


def task_host(host):
    """
    Prints current running host to screen
    """
    print('\n   HOST ' + Style.BRIGHT + host + Style.RESET_ALL + '\n')


def start():
    """
    Prints out some debug for starting a lib task
    """
    module_name = ''
    function_name = ''
    stack = inspect.stack()
    parentframe = stack[1][0]
    module = inspect.getmodule(parentframe)
    if module:
        module_pieces = (module.__name__).split('.')
        module_name = module_pieces[-1].capitalize()
    function_name = stack[1][3]
    title = f'Starting {module_name}.{function_name}()'
    dashes = '-' * (49-len(title))
    print(Fore.GREEN + f'{title} {dashes}' + Style.RESET_ALL)


def done(error = ''):
    """
    Prints out some debug for finishing a lib task
    """
    module_name = ''
    function_name = ''
    stack = inspect.stack()
    parentframe = stack[1][0]
    module = inspect.getmodule(parentframe)
    if module:
        module_pieces = (module.__name__).split('.')
        module_name = module_pieces[-1].capitalize()
    function_name = stack[1][3]
    title = f'{module_name}.{function_name}()'
    if (error == ''):
        print(Fore.GREEN + f'... done {title}' + Style.RESET_ALL)
    else:
        print(Fore.RED + f'... NOT done {title} - {error}' + Style.RESET_ALL)


def timestamp(filename = ""):
    """
    Gets timestamp in a known format
    """
    date_string = time.strftime("%Y-%m-%d.%H:%M:%S") # "%d/%m/%Y"
    if (filename != ""):
        return f'filename.{date_string}'
    else:
        return f'{date_string}'


def title(title, color = ''):
    """
    Print titles
    """
    #print(Fore.RED + 'some red text' + Style.RESET_ALL)
    print('==================================================')
    print(Fore.GREEN + title + Style.RESET_ALL)
    print('==================================================')


def exit(c, error):
    """
    Display error and host in red
    """
    host = Style.DIM + 'No host' + Style.RESET_ALL
    if c and c.has_key('host'):
        host = Fore.RED + c.host + Style.RESET_ALL
    elif isinstance(c, basestring):
        host = Fore.RED + c + Style.RESET_ALL
    print(Back.RED + ' FATAL ' + Style.RESET_ALL + ' ' + host)
    raise Exit('        ' + error)


# ==============================================================================
# Deprecated
# Most of these have moved to the custom Connection class that we are using
# that is in __init__.py
# ==============================================================================

def x_build_server_names():
    """
    Merge multiple entries for server names (usually an array)
    into a string suitable for nginx.  The first element will
    be the most specific, the last one is the generic

    For nginx:

        server_names wants to be specific to generic "bare"

    For letsencrypt:

        cli would prefer generic to specific "bare" first
        https://www.digitalocean.com/community/tutorials/how-to-set-up-let-s-encrypt-certificates-for-multiple-apache-virtual-hosts-on-ubuntu-14-04
        -d test.com -d www.test.com
    """
    server_names = env.config.get("server_names")[env.server_role]
    if server_names is None:
        server_names = [env.host_string]
    else:
        if not (isinstance(server_names, list)):
            server_names = [server_names]
            server_names.insert(0, env.host_string)
        else:
            server_names.insert(0, env.host_string)
    #print server_names
    #server_names = list(set(server_names))
    #print server_names
    return server_names


def x_template(filename):
    """
    Gets the local template from the packages/module folder
    """
    module_name = ''
    stack = inspect.stack()
    parentframe = stack[1][0]
    module = inspect.getmodule(parentframe)
    if module:
        module_pieces = (module.__name__).split('.')
        module_name = module_pieces[-1]
        return f'fabfile/packages/{module_name}/{filename}'
    else:
        return f'fabfile/packages/{filename}'

def x_enabled(config, module):
    """
    Set if a module/feature is enabled or not
    """
    return config.get('enables').get(module, False)

def x_environment(config):
    """
    Gets the environment
    """
    environment = config.get('environment')
    return environment

def x_is_production(config):
    """
    See if server is in production
    """
    environment = config.get('environment')
    if (environment == 'PRODUCTION'):
        return True
    else:
        return False

def x_sed(c, filename, search, replace, sudo = False, mustache = False):
    """
    Remote sed
    https://stackoverflow.com/questions/55044243/how-to-make-changes-edit-on-a-file-present-on-remote-server-using-python-fabric
    3/12/21 CG: Wanted to use f-strings here but we can't get it to work, I am suspecting
    that this is because we are using a backport of the f-strings for python 2.7 so the
    backport package of `future-fstrings` may have a bug in it as we do the crazy curly
    brackets for our mustache-like tokens.  Once we fully move to python 3.6, we should
    investigate putting the commented out f-string version back in play
    """
    # (1) Make sure file exists
    if not files.exists(c, filename):
        print(f'Filename: {filename} does not exist')
        return
    # (2) Build the sed command
    if mustache:
        # (2.1) If mustache, add the curly brackets
        command = 'sed -i "s/{{{{{0}}}}}/{1}/g" '.format(search, replace) +filename
    else:
        # (2.2) Raw replace
        command = f'sed -i "s/{search}/{replace}/g" ' +filename
    # (3) Run in sudo mode or normal
    if sudo:
        c.sudo(command)
    else:
        c.run(command)
