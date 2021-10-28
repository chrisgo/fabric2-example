import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Resque

This also installs basic ruby stuff, including rbenv so that we can
isolate the ruby and gem installs to a known version and not need to
use sudo gem install (only gem install)
The ruby install stuff comes from here:
https://linuxize.com/post/how-to-install-ruby-on-debian-9/
<del>https://www.digitalocean.com/community/tutorials/how-to-install-ruby-on-rails-with-rbenv-on-ubuntu-14-04</del>
"""

def install(c):
    util.start()
    # New Ruby install using rbenv (this takes a while)
    # https://linuxize.com/post/how-to-install-ruby-on-debian-9/
    c.sudo('apt-get install -yq git curl libssl-dev libreadline-dev zlib1g-dev')
    c.sudo('apt-get install -yq autoconf bison build-essential')
    c.sudo('apt-get install -yq libyaml-dev libreadline-dev libncurses5-dev libffi-dev libgdbm-dev')
    c.run_with_cd('~', f'echo \'export PATH="/home/{c.config.project.username}/.rbenv/bin:$PATH"\' >> ~/.bashrc')
    c.run_with_cd('~', 'echo \'eval "$(rbenv init -)"\' >> ~/.bashrc')
    c.run_with_cd('~', 'source ~/.bashrc')
    c.run_with_cd('~', f'echo \'export PATH="/home/{c.config.project.username}/.rbenv/bin:$PATH"\' >> ~/.bash_profile')
    c.run_with_cd('~', 'echo \'eval "$(rbenv init -)"\' >> ~/.bash_profile')
    c.run_with_cd('~', 'source ~/.bash_profile')
    #
    # 01/21/20 CG: There is still something wrong with this part of the install
    # The whole install will fail with the following:
    #
    # Fatal error: run() received nonzero return code 1 while executing!
    # Requested: curl -sL https://github.com/rbenv/rbenv-installer/raw/master/bin/rbenv-installer | bash -
    # Executed: /bin/bash -l -c "cd ~ >/dev/null && curl -sL https://github.com/rbenv/rbenv-installer/raw/master/bin/rbenv-installer | bash -"
    #
    # Aborting.
    #
    # The fix is to just run the "server_setup" again and the 2nd time around, it
    # will install fine (takse a while though
    #
    c.run_with_cd('~', 'curl -sL https://github.com/rbenv/rbenv-installer/raw/master/bin/rbenv-installer | bash -')
    version = '2.6.5'  # check ruby-lang.org
    c.run(f'rbenv install {version}')
    c.run(f'rbenv global {version}')
    c.run('ruby -v')
    c.run("echo 'gem: --no-document\' > ~/.gemrc")
    c.run('gem install bundler')
    c.run('gem install json')
    c.run('gem install resque')
    c.run('gem install unicorn')
    # Try to install new tabs on the resque UI
    # As of 7/2/19, still cannot get this to work
    # https://github.com/mattgibson/resque-scheduler-web
    # https://github.com/resque/resque-scheduler/issues/301
    c.run('gem install resque-scheduler-web')
    util.done()


def configure(c):
    util.start()
    # Create the resque-web directory structure
    c.sudo('mkdir -p /etc/unicorn')
    c.sudo('mkdir -p /var/www/resque-web')
    c.sudo('mkdir -p /var/www/resque-web/shared')
    c.sudo('mkdir -p /var/www/resque-web/config')
    c.sudo('mkdir -p /var/www/resque-web/log')
    c.sudo('mkdir -p /var/www/resque-web/shared')
    c.sudo('chown -R www-data:www-data /var/www/resque-web')
    c.sudo('chmod -R 775 /var/www/resque-web')
    c.put_template('etc-init.d-unicorn', '/etc/init.d/unicorn', sudo=True)
    c.put_template('etc-nginx-resque-web', '/etc/nginx/sites-available/resque-web', sudo=True)
    c.put_template('etc-unicorn-resque-web.conf', '/etc/unicorn/resque-web.conf', sudo=True)
    c.put_template('var-www-config.ru', '/var/www/resque-web/config.ru', sudo=True)
    c.put_template('var-www-unicorn.rb', '/var/www/resque-web/config/unicorn.rb', sudo=True)
    c.put_template('var-www-resque.rb', '/var/www/resque-web/config/resque.rb', sudo=True)
    # Get some env variables
    project_name = c.config.project.name.lower()
    # Munge the server_names to create a unique list
    # TODO: Move to separate function
    server_names = env.config.get('server_names', "")
    if (server_names != "" and 'resque' in server_names and server_names['resque'] != ""):
        server_names = server_names['resque']
        server_names.append(c.host)
        server_names = set(server_names)
        nginx_server_name = " ".join(server_names)
    else:
        nginx_server_name = c.host
    print(f'Setting nginx server_name: {nginx_server_name}')
    c.sed('/etc/nginx/sites-available/resque-web', '{{localhost}}', nginx_server_name, sudo=True)
    # Get the Letsencrypt cert up to the nginx
    c.sed('/etc/nginx/sites-available/resque-web', '{{project_name}}', c.config.project.name, sudo=True)
    #util.sed(c, '/etc/nginx/sites-available/resque-web', '{{project_name}}', c.config.project.name, sudo=True)
    # Configure resque to the correct Redis server
    redis_host = 'localhost'
    redis_port = 6379
    redis_password = env.password
    if (c.config.redis.host and c.config.redis.host != ''):
        redis_host = c.config.redis.host
        redis_port = c.config.redis.port
        redis_password = c.config.redis.password
        print(f'Using redis server @ {redis_host}:{redis_port}')
    c.sed('/var/www/resque-web/config.ru', '{{host}}', redis_host, sudo=True)
    c.sed('/var/www/resque-web/config.ru', '{{port}}', redis_port, sudo=True)
    c.sed('/var/www/resque-web/config.ru', '{{password}}', redis_password, sudo=True)
    # Continue configuring resque server
    c.sed('/var/www/resque-web/config/resque.rb', '{{password}}', c.config.project.password, sudo=True)
    c.sed('/var/www/resque-web/config.ru', '#{{namespace}}', f'Resque.redis.namespace = "{c.config.project.name}"', sudo=True)
    if not c.exists('/etc/nginx/sites-enabled/resque-web'):
        c.sudo('ln -s /etc/nginx/sites-available/resque-web /etc/nginx/sites-enabled/resque-web')
    # Do token replacement on the resque-web nginx for SSL cert
    ssl_cert = f'/etc/letsencrypt/live/{c.config.project.name}.com/fullchain.pem'
    ssl_cert_key = f'/etc/letsencrypt/live/{c.config.project.name}.com/privkey.pem'
    # Replace token
    c.sed('/etc/nginx/sites-available/resque-web', '{{ssl_cert}}', ssl_cert, sudo=True)
    c.sed('/etc/nginx/sites-available/resque-web', '{{ssl_cert_key}}', ssl_cert_key, sudo=True)
    c.sudo('chown root:root /etc/init.d/unicorn')
    c.sudo('chmod 775 /etc/init.d/unicorn')
    # Have unicorn (resque-web) start on boot
    c.sudo('update-rc.d unicorn defaults')
    # Restart unicorn and nginx
    c.sudo('/etc/init.d/unicorn restart')
    c.sudo('/etc/init.d/nginx restart')
    util.done()


def namespace(c, namespace):
    util.start()
    if (c.exists('/var/www/resque-web/config.ru')):
        c.sudo('rm /var/www/resque-web/config.ru')
    c.put_template('var-www-config.ru', '/var/www/resque-web/config.ru', sudo=True)
    # Configure resque to the correct Redis server
    redis_host = 'localhost'
    redis_port = 6379
    redis_password = c.config.project.password
    if (c.config.redis.host and c.config.redis.host != ''):
        redis_host = c.config.redis.host
        redis_port = c.config.redis.port
        redis_password =c.config.redis.password
        print(f'Using redis server @ {redis_host}:{redis_port}')
    c.sed('/var/www/resque-web/config.ru', '{{host}}', redis_host, sudo=True)
    c.sed('/var/www/resque-web/config.ru', '{{port}}', redis_port, sudo=True)
    c.sed('/var/www/resque-web/config.ru', '{{password}}', redis_password, sudo=True)
    #sed('/var/www/resque-web/config.ru', '{{password}}', redis_password, sudo=True)
    c.sed('/var/www/resque-web/config.ru', '#{{namespace}}', f'Resque.redis.namespace = "{namespace}"', sudo=True)
    c.sudo('/etc/init.d/unicorn restart')
    util.done()
