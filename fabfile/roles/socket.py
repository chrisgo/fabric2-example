import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.packages import *

"""
Socket Server for real time application
Currently, we are trying out swoole
https://www.swoole.co.uk

Other possibilities are
Ratchet: http://socketo.me/
AMP: https://amphp.org

https://www.reddit.com/r/PHP/comments/bmrfiq/reactphp_vs_swoole_vs_ratchet_vs_amp_which_do_you/
"""

def server(c):
    """
    Setup "socket" role
    """
    print(white('=================================================='))
    print(white('Building Socket Server'))
    print(white('=================================================='))
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Run apt update
    c.sudo('apt-get update')
    # Nginx & PHP
    nginx.install(c)
    php.install(c)
    nginx.configure(c)
    php.configure(c)
    # Papertrail
    if (util.enabled(c.config, 'papertrail')):
        papertrail.install()
        papertrail.configure()
    # S3FS
    #if (util.enabled(c.config, 's3fs')):
    #    s3fs.install()
    #    s3fs.configure()
    #swoole.install()
    #swoole.install()
    #centrifugo.install()
    #centrifugo.configure()
    print(white('=================================================='))
    print(white('... done Building Socket Server'))
    print(white('=================================================='))


def project(c):
    """
    """
    print(white('=================================================='))
    print(white('Setup/Install Project on Socket Server'))
    print(white('=================================================='))
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Run update
    print(white('=================================================='))
    print(white('... done Setup/Install Project on Socket Server'))
    print(white('=================================================='))


def release(c, branch=''):
    """
    Release code to an environment
    """
    print(white('=================================================='))
    print(white('Release Project on Socket Server'))
    print(white('=================================================='))
    # Deploy build
    #print("BRANCH: %s" % branch)
    #if (branch == ''):
    print(green("Deploy Build [HEAD] ..."))
    #else:
    #    print("Deploy Build [***** From Branch: %s *****] ..." % branch)
    project_dir = f'{c.config.project.dir.lower()}{c.config.project.name.lower()}'
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
    c.sed('%s/application/config/app.php' % env.server_root, '{{BUILD.DATE}}', build_date)
    # Configure system
    c.run(f'php /var/www/{c.config.project.name}/php/minion System_Configure')
    # Update Letsencrypt SSL Cert
    #if util.enabled(c.config, 'ssl') and util.enabled(c.config, 'letsencrypt'):
    #    put('fabfile/environments/ssl/letsencrypt/privkey.pem', '/etc/letsencrypt/live/{c.config.project.name}.com', use_sudo=True)
    #    put('fabfile/environments/ssl/letsencrypt/fullchain.pem', '/etc/letsencrypt/live/{c.config.project.name}.com', use_sudo=True)
    #    c.sudo('/etc/init.d/nginx restart')
    print(white('=================================================='))
    print(white('... done Release Project on Socket Server'))
    print(white('=================================================='))
