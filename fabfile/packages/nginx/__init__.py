import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Nginx
"""

def install(c):
    util.start()
    c.sudo('apt-get install -yq nginx')
    util.done()


def configure(c):
    util.start()
    # Nginx conf changes
    c.sed('/etc/nginx/nginx.conf', '# server_names_hash_bucket_size 64', 'server_names_hash_bucket_size 64',sudo=True)
    # Send the dhparam.pem file up to the server
    if not c.exists('/etc/nginx/dhparam.pem'):
        c.put_template('dhparam.pem', '/etc/nginx/dhparam.pem', sudo=True)
    # Nginx breaks due to 2 port 80 listeners
    c.sed('/etc/nginx/sites-available/default', 'listen ', '#listen ', sudo=True)
    # Restart nginx
    c.sudo('/etc/init.d/nginx restart')
    # Load up check.php for Amazon health check
    # put_template('check.php', '/usr/share/nginx/html/check.php', sudo=True)
    # 10/03/19 CG: Put this back to /var/www/html
    #put_template('check.php', '/var/www/html/check.php', sudo=True)
    # 01/20/20 CG: This somehow went back to /usr/share/nginx/html/check
    c.put_template('check.php', '/usr/share/nginx/html/check.php', sudo=True)
    util.done()


def add_host(c, environment = "DEVELOPMENT"):
    """
    Add a host

    TODO: Fix bug where it is dumping too many server names
        on the www_root variable (additive from the list)
    """
    util.start()
    _project_name = c.config.project.name.lower()
    _www_root = c.config.project.server.public_dir
    _version = c.config.php.version
    # Array of server names
    _server_names = c.build_server_names()
    # Add new virtual host
    print('Adding new virtual host: %s' % _server_names[0])
    # Delete old virtual host file
    if c.exists(f'/etc/nginx/sites-available/{_project_name}', sudo=True):
        print('Found old virtual host, archiving')
        orig = f'/etc/nginx/sites-available/{_project_name}'
        timestamp = util.timestamp(_project_name)
        backup = f'/etc/nginx/sites-available/{timestamp}'
        c.sudo(f'mv {orig} {backup}')
        #sudo('rm -fR /etc/nginx/sites-available/%s' % project_name)
        c.sudo(f'rm -fR /etc/nginx/sites-enabled/{_project_name}')
    # Deal with SSL portion of site
    # For vagrant, we do self-signed certificates
    print('Checking for HTTPS/SSL')
    if c.enabled('ssl'):
        nginx_site_file = 'nginx-site-ssl';
    else:
        nginx_site_file = 'nginx-site';
    print('Done with SSL stuff, copying nginx sites-available files')
    c.put_template(nginx_site_file, f'/etc/nginx/sites-available/{_project_name}', sudo=True)
    print('Replacing some tokens')
    # TODO: Token needs to be sync'd with Vagrantfile share folders
    # TODO: Token needs to by sync'd with dev_chris.py
    # TODO: Token needs to by sync'd with main fabric __init__.py
    # Need to escape www_root
    c.sed(f'/etc/nginx/sites-available/{_project_name}', '{{www_root}}', util.sed_escape(_www_root), sudo=True)
    c.sed(f'/etc/nginx/sites-available/{_project_name}', '{{php_version}}', util.sed_escape(_version), sudo=True)
    # Munge the server_names to create a unique list
    # TODO: Move to separate function
    print(f'Setting nginx server_name: {" ".join(_server_names)}')
    c.sed(f'/etc/nginx/sites-available/{_project_name}', '{{localhost}}', " ".join(_server_names), sudo=True)
    c.sed(f'/etc/nginx/sites-available/{_project_name}', '{{environment}}', c.config.environment, sudo=True)
    # SSL Certificate
    _ssl_cert = f'/etc/letsencrypt/live/{_project_name}.com/fullchain.pem'
    _ssl_cert_key = f'/etc/letsencrypt/live/{_project_name}.com/privkey.pem'
    if c.config.provider == 'vagrant':
        _ssl_cert = f'/vagrant/{_project_name}/ssl/fullchain.pem'
        _ssl_cert_key = f'/vagrant/{_project_name}/ssl/privkey.pem'
    # Replace token
    c.sed(f'/etc/nginx/sites-available/{_project_name}', '{{ssl_cert}}', util.sed_escape(_ssl_cert), sudo=True)
    c.sed(f'/etc/nginx/sites-available/{_project_name}', '{{ssl_cert_key}}', util.sed_escape(_ssl_cert_key), sudo=True)
    util.done()
