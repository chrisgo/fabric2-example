import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.packages import *
from ..core import util

# www role

def server(c):
    """
    Setup Web+App Server with basic software for "www" role
    """
    print('==================================================')
    print('Building Web+App Server')
    print('==================================================')
    # Run apt update
    c.sudo('apt-get update')
    # Nginx & PHP
    nginx.install(c)
    php.install(c)
    nginx.configure(c)
    php.configure(c)
    # Papertrail
    if (c.enabled('papertrail')):
        papertrail.install(c)
        papertrail.configure(c)
    # S3FS
    if (c.enabled('s3fs')):
        s3fs.install(c)
        s3fs.configure(c)
    # Supervisor
    supervisor.install(c)
    print('==================================================')
    print('... done Building Web+App Server')
    print('==================================================')


def project(c):
    """
    Installs and setup web+app server with project specifics

    This could include:
    (1) Checking out source code for the first time
        - more work than you would think
    (2) Change web server document root
    (3) Mounting S3 file systems
    (4) Setting timezone
    (5) Possibly refresh database from latest backup
    (6) Install other non-standard software like PEAR
    """
    print('==================================================')
    print('Setup/Install Project on Web+App Server')
    print('==================================================')
    # Get some variables from the environment
    print("Setting up environment ...")
    _version = c.config.php.version
    _project_name = c.config.project.name.lower()
    _mount_root = c.config.mount_root
    #server_root     = env.config.get('server_root', "")
    #www_root        = env.config.get('www_root', "")
    _aws_buckets = c.config.aws.buckets
    #app_dirs = c.config.project.app_dirs
    #project_name = c.config.project.name
    # Checkout project from git
    if (c.config.provider != 'vagrant'):
        print("Checking out project from git")
        git.register(c)
        git.checkout(c)
        git.rsync(c)
        # Also create the logs and cache folders
        _server_root_dir = c.config.project.server.root_dir
        c.run(f'mkdir -m 777 -p {_server_root_dir}/application/logs')
        c.run(f'mkdir -m 777 -p {_server_root_dir}/application/cache')
    else:
        print("Vagrant project directory already created during VM boot in Vagrantfile")
        print("  Guest: /var/www/<project>/web")
        print("  Host:  ~/Projects/<project>/src/php/public")
    # Add host to nginx
    nginx.add_host(c, c.config.environment)
    # Symlink to enable site
    print('Creating symlink to project virtual host')
    c.sudo(f'ln -s /etc/nginx/sites-available/{_project_name} /etc/nginx/sites-enabled/{_project_name}')
    # Restart
    print('Restart nginx & php-fpm')
    c.sudo('/etc/init.d/nginx restart')
    c.sudo(f'/etc/init.d/php{_version}-fpm restart')
    # Mount project folders (whatever is defined)
    print("Mounting project directories ...")
    # Mount S3
    if (c.enabled('s3fs')):
        print('s3fs enabled')
        #s3fs.mount(c, mount_root, aws_buckets)
    else:
        print("NOT mounting S3FS")
    # Create directories for the project/application
    print("Creating project directories")
    if c.config.project.dirs:
        directories = []
        for _dir in c.config.project.dirs:
            directories.append(f'{_mount_root}/{_dir}')
        print(directories)
        #filesystem.mkdirs(c, directories)
    # Also make /tmp/{{domain}} directory
    c.run(f'mkdir /tmp/{_project_name}')
    c.run(f'chmod -R 777 /tmp/{_project_name}')
    # ==================================================
    # Install other software here
    # ==================================================
    print("Installing project-specific software ...")
    if c.config.project.packages:
        for _package in c.config.project.packages:
            print(f'  ... {_package}')
            c.sudo(f'apt-get install -yq {_package}')
    print('==================================================')
    print('... done Setup/Install Project on Web+App Server')
    print('==================================================')


def release(c, branch=''):
    """
    Release code to an environment
    """
    print('==================================================')
    print('Release Project on Web+App Server')
    print('==================================================')
    _project_name = c.config.project.name
    _server_root = f'/var/www/{_project_name}/php'
    # Checkout
    c.run_with_cd(f'~/projects/{_project_name}', 'git checkout')
    c.run_with_cd(f'~/projects/{_project_name}', 'git reset --hard origin/master')
    c.run_with_cd(f'~/projects/{_project_name}', 'git clean -f -d')
    # Rsync
    source = f'~/projects/{_project_name}/src/php'
    target = server_root
    c.run(f'rsync -oavz {source}/ {target}')
    c.run('git pull')
    # Perms
    c.sudo(f'chmod -R 777 {_server_root}/storage')
    c.sudo(f'chmod -R +t {_server_root}/storage')
    c.sudo(f'chmod -R 777 {_server_root}/bootstrap/cache')
    c.sudo(f'chmod -R +t {_server_root}/bootstrap/cache')
    c.sudo(f'sudo setfacl -R -d -m u:www-data:rwx,g:www-data:rwx {_server_root}/bootstrap/cache')
    # Delete packages.php and services.php
    #run('rm %s/bootstrap/cache/services.php' % server_root)
    #run('rm %s/bootstrap/cache/packages.php' % server_root)
    # add the facl again
    # Run commands
    #run('npm rebuild node-sass')
    #run('npm run prod')
    # run('php artisan optimize')
    c.run_with_cd(f'{_server_root}', 'php artisan view:clear')
    #run('php artisan cache:clear')
    #run('php artisan config:clear')
    # Change permissions and add facl again
    c.sudo(f'chmod -R 777 {_server_root}/bootstrap/cache/services.php')
    c.sudo(f'chmod -R 777 {_server_root}/bootstrap/cache/packages.php')
    c.sudo(f'sudo setfacl -R -d -m u:www-data:rwx,g:www-data:rwx {_server_root}/bootstrap/cache')
    # Update build date
    build_date = datetime.datetime.now().strftime("%m/%d/%y %I:%M %p %Z")
    print(f'Updating build date to {build_date}')
    c.sed(f'{_server_root}/config/project.php', '{{build_date}}', build_date)
    # Restart worker/supervisor
    c.sudo('/etc/init.d/supervisor restart')
    print("... done release()")


def configure(c):
    """
    Configure Server
    """
    print('==================================================')
    print('Configure Project on Web+App Server')
    print('==================================================')
    c.run(f'php /var/www/{c.config.project.name}/php/minion System_Configure')
    print('==================================================')
    print('... done Configure Project on Web+App Server')
    print('==================================================')
