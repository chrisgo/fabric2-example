import datetime
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *
from fabfile.packages import *

"""
Node server

The node server serves a couple of things for our technology stack

(1) Web Scraping: using Nightmarejs
(2) Websockets:   using socket.io

In order to facilitate these tasks, the node server should also
provide an API endpoint for the PHP code to call it.  Originally, we
were going to use resque to push jobs through but that requires
setting up queues that will collide with the workers.  Having an API
endpoint can hide this implementation detail and still enable the
node code to perform the jobs async using the node-resque library

The node code will run inside pm2 and be proxied behind nginx
Security will be handled via JWT (JSON Web Tokens)

API Endpoints

https://prd-nod1.{_project_name}.com/nodejs     (where nightmarejs runs)
https://prd-nod1.{_project_name}.com/socketio

TODO:

(1) Do we run one server (shared codebase) or separate node projects?
    - For now, due to websockets, I think it has to be separate

(2) How to call this using private IP inside same DO datacenter?
    - Just call IP without SSL

"""

def server(c):
    """
    Setup Nodejs with basic software for "node" role
    """
    print('==================================================')
    print('Building Node Server')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Set the user
    #env.user = env.base_user
    #env.password = env.base_password
    # Run apt update
    c.sudo('apt-get update')
    # Install nginx
    nginx.install(c)
    nginx.configure(c)
    # Install node
    nodejs.install(c)
    nodejs.configure(c)
    # Install pm2
    pm2.install(c)
    pm2.configure(c)
    # Papertrail
    if (util.enabled(c.config, 'papertrail')):
        papertrail.install(c)
        papertrail.configure(c)
    # S3FS
    if (util.enabled(c.config, 's3fs')):
        s3fs.install(c)
        s3fs.configure(c)
    print('==================================================')
    print('... done Building Node Server')
    print('==================================================')


def project(c):
    """
    Installs and setup Nodejs server with project specifics
    """
    print('==================================================')
    print('Setup/Install Project on Node Server')
    print('==================================================')
    c.sudo('export DEBIAN_FRONTEND=noninteractive')
    # Get some variables from the environment
    print("Setting up environment ...")



    provider = env.config.get('provider')


    provider = env.config.get('provider')
    mount_root = env.config.get('mount_root', "/tmp/")
    if (provider != 'vagrant'):
        print("Checking out project from git")
        git.register(c, env.git_server, env.user)
        git.checkout(c, env.git_project, env.project_dir, env.project_name)
        # Prepare rsync
        source = '%s%s/src/js/nodejs/' % (env.project_dir.lower(), env.project_name.lower())
        target = '%s/nodejs' % (env.server_root)
        # Check to make sure directory exists
        if not c.exists(target):
            print('Creating project folder for web server: %s' % target)
            c.sudo('mkdir -p %s' % target)
            c.sudo('chown -R %s:%s %s' % (env.user, env.user, target))
            c.sudo('chmod -R 775 %s' % target)
        #print "rsync -oavz %s %s" % (source, target)
        c.run("rsync -oavz %s %s" % (source, target))
    else:
        print("Vagrant project directory already created")
        print("during VM boot in Vagrantfile")
        print("Guest: /var/www/<project>/<module>")
        print("Host:  ~/Projects/<project>/src/js/<module>")
    # Figure out SSL
    print('Checking for HTTPS/SSL')
    #certbot.add_simple_host()
    # Then add the host files
    nodejs.nginx_proxy(c)
    # Restart nginx
    c.sudo('/etc/init.d/nginx restart')
    # Mount project folders (whatever is defined)
    # Mount S3
    # Create directories for the project/application
    # Start node servers
    #for folder in env.node_sources:
    #    project = os.path.basename(folder)
    #    cmd = 'pm2 delete /var/www/%s/%s/index.js -f --name="%s"'
    #    cmd = 'pm2 start /var/www/%s/%s/index.js -f --name="%s"'
    #    run(cmd % (env.project_name, project, project))
    c.run_with_cd(f'/var/www/{c.config.project.name}/nodejs', 'pm2 start apps.json')
    c.run_with_cd(f'/var/www/{c.config.project.name}/nodejs', 'pm2 save')
    # Create the startup script
    c.run('pm2 startup ubuntu -', warn_only=True)
    # Run the output from above as root to create startup scripts
    cmd = 'sudo su -c "env PATH=$PATH:/usr/bin pm2 startup ubuntu -u %s --hp /home/%s"'
    c.sudo(cmd % (env.project_name, env.project_name))
    c.sudo('/etc/init.d/pm2-init.sh restart')
    print('==================================================')
    print('... done Setup/Install Project on Node Server')
    print('==================================================')

def alt_project_setup(c):
    """
    Switch the pm2 user
    """
    util.start()
    #provider = c.config.provider
    #cmd = 'sudo su -c "env PATH=$PATH:/usr/bin pm2 startup ubuntu -u %s --hp /home/%s"'
    #if (provider != 'vagrant'):
    #    c.sudo(cmd % (env.project_name, env.project_name))
    #else:
    #    c.sudo(cmd % ('vagrant', 'vagrant')
    #c.run('pm2 save')
    #c.sudo('/etc/init.d/pm2-init.sh restart')
    util.done()

def release(c, branch=''):
    """
    Release code to an environment
    """
    print('==================================================')
    print('Release Project on Node Server')
    print('==================================================')
    # Deploy build
    #print("BRANCH: %s" % branch)
    #if (branch == ''):
    print('Deploy Build [HEAD] ...')
    #else:
    #    print("Deploy Build [***** From Branch: %s *****] ..." % branch)
    project_dir = f'{env.project_dir.lower()}{env.project_name.lower()}'
    #run('git checkout %s' % branch)
    c.run_with_cd(project_dir, 'git checkout')
    c.run_with_cd(project_dir, 'git reset --hard origin/master')
    c.run_with_cd(project_dir, 'git clean -f -d')
    c.run_with_cd(project_dir, 'git pull')
    # Rsync code
    print('Performing rsync to %s' % env.server_root)
    source = '%s%s/src/js/nodejs' % (env.project_dir.lower(), env.project_name.lower())
    target = f'/var/www/{c.config.project.name}/nodejs' #'%s/../nodejs' % env.www_root
    c.run_with_cd(project_dir, "rsync -oavz --delete %s/ %s" % (source, target))
    # Update build date
    #build_date = datetime.datetime.now().strftime("%m/%d/%y %I:%M %p %Z")
    #print("Updating build date to %s" % build_date)
    #sed('%s/application/config/app.php' % env.www_root,
    #    '\{\{BUILD.DATE\}\}',
    #    build_date)
    # Restart the node process
    #run('pm2 start apps.json')
    #run('pm2 save')
    c.run_with_cd(f'/var/www/{c.config.project.name}/nodejs', 'pm2 reload all')
    #c.sudo('/etc/init.d/pm2-init.sh reload')
    # Restart nginx (this also make sure the letsencrypt certificate gets reloaded)
    c.sudo('/etc/init.d/nginx restart')
    print('==================================================')
    print('... done Release Project on Node Server')
    print('==================================================')

@task
def configure(c):
    """
    Configure Server
    """
    print('==================================================')
    print('Configure Project on Node Server')
    print('==================================================')
    print('Replacing tokens in apps.json')
    c.sed(f'/var/www/{c.config.project.name}/nodejs/apps.json', 'chris-local', 'production')
    c.sed(f'/var/www/{c.config.project.name}/nodejs/apps.json', '"watch": true,', '"watch": false,')
    print('Reloading apps.json')
    c.run_with_cd(f'/var/www/{c.config.project.name}/nodej', 'pm2 start apps.json')
    c.run_with_cd(f'/var/www/{c.config.project.name}/nodej', 'pm2 save')
    c.sudo('/etc/init.d/pm2-init.sh restart')
    print('==================================================')
    print('... done Configure Project on Node Server')
    print('==================================================')
