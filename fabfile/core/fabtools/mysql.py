# import datetime
# from fabric2 import Connection
# from invoke import Collection
# from fabric2 import Config
# from fabric2 import task
# from patchwork import files
from pipes import quote
# from fabfile.core import *
import pprint
import importlib
import os
import sys
from invoke import Collection
from fabric import Config
from fabric import task

# ==============================================================================
# Helper functions that used to be in fabtools
# Taken from https://github.com/fabtools/fabtools/blob/master/fabtools/mysql.py
# ==============================================================================

def database_exists(c, name, **kwargs):
    """
    Check if a MySQL database exists.
    """
    res = query(c, f"SHOW DATABASES LIKE '{name}';", **kwargs)
    #with settings(
    #        hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
    #    res = query("SHOW DATABASES LIKE '%(name)s';" % {
    #        'name': name
    #    }, **kwargs)
    #return res.succeeded and (res == name)

def query(c, query, sudo=True, **kwargs):
    """
    Run a MySQL query.
    """
    #func = use_sudo and run_as_root or run
    user = kwargs.get('mysql_user')
    password = kwargs.get('mysql_password')
    func_mysql = 'mysql'
    mysql_host = kwargs.get('mysql_host')
    print(f'{user} | {password} | {mysql_host}')
    #return
    options = [
        '--batch',
        '--raw',
        '--skip-column-names',
    ]
    if user:
        options.append(f'--user={quote(user)}')
    if password:
        #if not is_installed('sshpass'):
        #    install('sshpass')
        func_mysql = f'sshpass -p {quote(password)} mysql'
        options.append('--password')
    if mysql_host:
        options.append(f'--host={quote(mysql_host)}')
    options = ' '.join(options)
    #return func('%(cmd)s %(options)s --execute=%(query)s' % {
    #    'cmd': func_mysql,
    #    'options': options,
    #    'query': quote(query),
    #})
    command = f'{func_mysql} {options} --execute={quote(query)}'
    print(command)
    #return
    if (sudo):
        return c.sudo(command)
    else:
        a = c.run(command)
        print(a)


def user_exists(c, name, host='localhost', **kwargs):
    """
    Check if a MySQL user exists.
    """
    res = query("""
        use mysql;
        SELECT COUNT(*) FROM user WHERE User = '{name}' AND Host = '{host}';
        """, **kwargs)
    return res.succeeded and (int(res) == 1)


def create_user(c, name, password, host='localhost', **kwargs):
    """
    Create a MySQL user.

    Example::

        import fabtools

        # Create DB user if it does not exist
        if not fabtools.mysql.user_exists('dbuser'):
            fabtools.mysql.create_user('dbuser', password='somerandomstring')

    """
    query(c, f"CREATE USER '{name}'@'{host}' IDENTIFIED BY '{password}';", **kwargs)
    puts(f"Created MySQL user '{name}'.")


def create_database(c, name, owner=None, owner_host='localhost', charset='utf8mb4',
                    collate='utf8mb4_general_ci', **kwargs):
    """
    Create a MySQL database.

    Example:

        import fabtools

        # Create DB if it does not exist
        if not fabtools.mysql.database_exists('myapp'):
            fabtools.mysql.create_database('myapp', owner='dbuser')

    """
    query(c, f'CREATE DATABASE {name} CHARACTER SET {charset} COLLATE {collate}', **kwargs)
    if owner:
        grant_privileges(c, name, owner, owner_host, **kwargs)
    print(f'Created MySQL database: {name}')


def grant_privileges(c, name, owner=None, owner_host='localhost',
                     privileges='ALL PRIVILEGES', **kwargs):
    """
    Grant privileges for database
    """
    _password = kwargs.get('mysql_password')
    command = f"GRANT {privileges} ON {name}.* " \
              f"TO '{owner}'@'{owner_host}' IDENTIFIED BY '{_password}' WITH GRANT OPTION;"
    print(command)
    query(c, command, **kwargs)
    print(f'Privelege granted to {name} for user {owner}@{owner_host}')
