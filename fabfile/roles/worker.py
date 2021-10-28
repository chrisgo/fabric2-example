import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.packages import *


"""
Worker Server Build and Setup
"""
def server(c):
    """
    Setup Worker Server with basic software for "worker" role
    """
    print(white('=================================================='))
    print(white('Building Worker Server'))
    print(white('=================================================='))
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Run apt update
    c.sudo('apt-get update')
    # Nginx & PHP
    nginx.install()
    php.install()
    nginx.configure()
    php.configure()
    # Install php-resque
    php_resque.install()
    php_resque.configure()
    # Papertrail
    if (util.enabled(c.config, 'papertrail')):
        papertrail.install()
        papertrail.configure()
    # S3FS
    if (util.enabled(c.config, 's3fs')):
        s3fs.install()
        s3fs.configure()
    print(white('=================================================='))
    print(white('... done Building Worker Server'))
    print(white('=================================================='))


"""
Project Setup
"""
def project(c):
    """
    """
    print(white('=================================================='))
    print(white('Setup/Install Project on Worker Server'))
    print(white('=================================================='))
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
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
    #nginx.add_host(env.config.get('environment', ""))
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
    print(white('=================================================='))
    print(white('... done Setup/Install Project on Worker Server'))
    print(white('=================================================='))

@task
def release(c, branch=''):
    """
    Release code to an environment
    """
    print(white('=================================================='))
    print(white('Release Project on Web+App Server'))
    print(white('=================================================='))
    # Deploy build
    #print("BRANCH: %s" % branch)
    #if (branch == ''):
    print(green("Deploy Build [HEAD] ..."))
    #else:
    #    print("Deploy Build [***** From Branch: %s *****] ..." % branch)
    project_dir = f'{c.config.project.dir}{c.config.project.name}'
    #run('git checkout %s' % branch)
    c.run_with_cd(project_dir, 'git checkout')
    c.run_with_cd(project_dir, 'git reset --hard origin/master')
    c.run_with_cd(project_dir, 'git clean -f -d')
    c.run_with_cd(project_dir, 'git pull')
    # Rsync code
    print('Performing rsync to %s' % env.server_root)
    source = '%s%s/%s' % (env.project_dir.lower(), env.project_name.lower(), env.source_root)
    target = env.server_root
    c.run_with_cd(project_dir, "rsync -oavz --delete \
                           --exclude 'application/log*' \
                           --exclude 'application/cache*' \
                           %s/ %s" %
                          (source, target))
    # Update build date
    build_date = datetime.datetime.now().strftime("%m/%d/%y %I:%M %p %Z")
    print("Updating build date to %s" % build_date)
    c.sed('%s/application/config/app.php' % env.server_root,
            '\{\{BUILD.DATE\}\}',
            build_date)
    # Configure system
    c.run(f'php /var/www/{c.config.project.name}/php/minion System_Configure')
    # Restart the workers
    print("Deleting php-minion-resque log ...")
    if c.exists('/var/log/php-minion-resque.log'):
        c.sudo('rm /var/log/php-minion-resque.log')
    print("Restarting php-minion-resque ...")
    c.sudo('/etc/init.d/php-minion-resque restart', pty=False)
    c.sudo('/etc/init.d/php-minion-resque-scheduler restart', pty=False)
    print(white('=================================================='))
    print(white('... done Release Project on Worker Server'))
    print(white('=================================================='))

@task
def freediskspace(c):
    """
    Free disk space
    """
    print(white('=================================================='))
    print(white('Free Disk Spacee on Web+App Server'))
    print(white('=================================================='))
    c.sudo_with_cd('/tmp', f'rm -fR s3fs-docs.{c.config.project.name}.com/')
    c.sudo_with_cd('/tmp', f'rm -fR s3fs.{c.config.project.name}.com/')
    print(white('=================================================='))
    print(white('... done Free Disk Space on Web+App Server'))
    print(white('=================================================='))

@task
def configure(c):
    """
    Configure Server
    """
    print(white('=================================================='))
    print(white('Configure Project on Worker Server'))
    print(white('=================================================='))
    c.run(f'php /var/www/{c.config.project.name}/php/minion System_Configure')
    print(white('=================================================='))
    print(white('... done Configure Project on Worker Server'))
    print(white('=================================================='))
