import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Git

We moved this to Gitlab.com on 11/29/2016 because git.velocimedia.com suddenly
died with gitolite (Perl has some TAINT insecure error)

In order to change it on existing servers, we need to do following:
- copy ~/.ssh/config
- copy ~/.ssh/id_rsa_deploy (private key file)
- ssh into the server:
  - cd ~/projects
  - rm -fR {_project_name}
  - git clone ssh://git@git-server/{_project_name}/main.git {_project_name}
- do a release

"""

def install(c):
    util.start()
    util.done()

def configure(c):
    util.start()
    util.done()


def rsync(c):
    """
    Rsyncs the checked out code to the right place

    checkout:
        root_dir:   ~/checkout                          # checkout dir
        source_dir: src/php                             # source folder
    server:
        root_dir:   /var/www/{{project}}/php            # Server root
        public_dir: /var/www/{{project}}/php/public     # Nginx web root

    """
    util.start()
    # (1) Set some convenience variables
    _checkout_root_dir = c.config.project.checkout.root_dir
    _checkout_source_dir = c.config.project.checkout.source_dir
    _server_root_dir = c.config.project.server.root_dir
    #_server_public_dir = c.config.project.server.public_dir
    # (2) Check to make sure directory exists
    if not c.exists(_server_root_dir):
        print(f'Creating project folder for web server: {_server_root_dir}')
        c.sudo(f'mkdir -p {_server_root_dir}')
        c.sudo(f'chown -R {c.config.project.username}:{c.config.project.username} {_server_root_dir}')
        c.sudo(f'chmod -R 775 {_server_root_dir}')
    # (3) Rsync the entire directory over
    print(f'Performing rsync to {_server_root_dir}')
    source = f'{_checkout_root_dir}/{c.config.project.name}/{_checkout_source_dir}'
    target = _server_root_dir
    c.run("rsync -oavz --exclude 'application/log*' " \
          " --exclude 'application/cache*' " \
          f'{source}/ {target}')
    c.run(f'mkdir -p {_server_root_dir}/application/cache')
    c.run(f'mkdir -p {_server_root_dir}/application/logs')
    c.run(f'chmod -R 777 {_server_root_dir}/application/cache')
    c.run(f'chmod -R 777 {_server_root_dir}/application/logs')
    util.done()


def checkout(c, branch = ''):
    """
    Checkout code
    """
    util.start()
    # Check out source code for the first time (always use master)
    print('Checking out code for the first time ...')
    print('********************************************************')
    print('*** Type yes on the next prompt to connect to server ***')
    print('********************************************************')
    _project_dir = c.config.project.checkout.root_dir
    _git_project = c.config.git.project
    if not c.exists(_project_dir):
        c.run(f'mkdir -p {_project_dir}')
    if not c.exists(f'{_project_dir}/{c.config.project.name}'):
        if (branch != '' and branch != None):
            command = f'git clone -b {branch} ssh://git@git-server/{_git_project} {c.config.project.name}'
        else:
            command = f'git clone ssh://git@git-server/{_git_project} {c.config.project.name}'
        c.run_with_cd(_project_dir, command)
    util.done()


def register(c):
    """
    Register git server and credentials
    """
    util.start()
    # (1) Copy the deploy private key to the server
    print('Copying deployment private key to server')
    c.put('fabfile/environments/git/id_rsa_deploy', f'/home/{c.config.project.username}/.ssh/id_rsa_deploy')
    c.run(f'chmod 0600 /home/{c.config.project.username}/.ssh/id_rsa_deploy')
    # (2) Copy ssh config file to server
    c.put_template('ssh_config', f'/home/{c.config.project.username}/.ssh/config')
    # (3) Replace tokens in config file
    c.sed(f'/home/{c.config.project.username}/.ssh/config', '{{git-server}}', c.config.git.host)
    c.sed(f'/home/{c.config.project.username}/.ssh/config', '{{home}}', c.config.project.username)
    # (4) Run git config
    c.run('git config --global core.preloadIndex false')
    util.done()
