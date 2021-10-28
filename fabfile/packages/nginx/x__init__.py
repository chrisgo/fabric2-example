# -*- coding: future_fstrings -*-
import datetime
from fabric2 import Connection
from invoke import Collection
from fabric2 import Config
from fabric2 import task
from patchwork import files
from fabfile.packages import util



"""
Nginx
"""

def install():
    util.start()
    sudo('apt-get install -yq nginx')
    util.done()

def configure():
    util.start()
    # Nginx conf changes
    c.sed('/etc/nginx/nginx.conf', '# server_names_hash_bucket_size 64', 'server_names_hash_bucket_size 64', sudo=True)
    # Send the dhparam.pem file up to the server
    if not c.exists('/etc/nginx/dhparam.pem'):
        c.put_template('dhparam.pem', '/etc/nginx/dhparam.pem', sudo=True)
    # Nginx breaks due to 2 port 80 listeners
    c.sed('/etc/nginx/sites-available/default', 'listen ', '#listen ', sudo=True)
    # Restart nginx
    c.sudo('/etc/init.d/nginx restart')
    # Load up check.php for Amazon health check
    # put(util.template('check.php'), '/usr/share/nginx/html/check.php', use_sudo=True)
    # 10/03/19 CG: Put this back to /var/www/html
    #put(util.template('check.php'), '/var/www/html/check.php', use_sudo=True)
    # 01/20/20 CG: This somehow went back to /usr/share/nginx/html/check
    c.put_template('check.php', '/usr/share/nginx/html/check.php', sudo=True)
    util.done()

"""
Add a host

TODO: Fix bug where it is dumping too many server names
      on the www_root variable (additive from the list)
"""
def add_host(environment = "DEVELOPMENT"):
    util.start()
    project_name = env.project_name.lower()
    www_root = env.www_root
    provider = env.config.get('provider')
    # Array of server names
    server_names = util.build_server_names()
    # Add new virtual host
    print('Adding new virtual host: %s' % server_names[0])
    # Delete old virtual host file
    if c.exists(f'/etc/nginx/sites-available/{project_name}'):
        print('Found old virtual host, archiving')
        orig = '/etc/nginx/sites-available/{project_name}'
        backup = '/etc/nginx/sites-available/{util.timestamp(project_name)}'
        sudo(f'mv {orig} {backup}')
        #sudo('rm -fR /etc/nginx/sites-available/%s' % project_name)
        sudo(f'rm -fR /etc/nginx/sites-enabled/{project_name}')
    # Deal with SSL portion of site
    # For vagrant, we do self-signed certificates
    print('Checking for HTTPS/SSL')
    if c.enabled('ssl'):
        nginx_site_file = "nginx-site-ssl";
    else:
        nginx_site_file = "nginx-site";
    print('Done with SSL stuff, copying nginx sites-available files')
    c.put_template(nginx_site_file, f'/etc/nginx/sites-available/{project_name}', sudo=True)
    print('Replacing some tokens')
    # TODO: Token needs to be sync'd with Vagrantfile share folders
    # TODO: Token needs to by sync'd with dev_chris.py
    # TODO: Token needs to by sync'd with main fabric __init__.py
    c.sed('/etc/nginx/sites-available/%s' % project_name,
        '{{www_root\}\}',
        '%s' % www_root,
        use_sudo=True, backup='.bak', flags='')
    # Munge the server_names to create a unique list
    # TODO: Move to separate function
    print("Setting nginx server_name: %s" % " ".join(server_names))
    sed('/etc/nginx/sites-available/%s' % project_name,
        '\{\{localhost\}\}',
        '%s' % " ".join(server_names),
        use_sudo=True, backup='.bak', flags='')
    sed('/etc/nginx/sites-available/%s' % project_name,
        '\{\{environment\}\}',
        '%s' % environment,
        use_sudo=True, backup='.bak', flags='')
    # SSL Certificate
    ssl_cert = "/etc/letsencrypt/live/%s.com/fullchain.pem" % project_name
    ssl_cert_key = "/etc/letsencrypt/live/%s.com/privkey.pem" % project_name
    # Replace token
    sed('/etc/nginx/sites-available/%s' % project_name,
        '\{\{ssl_cert\}\}',
        '%s' % ssl_cert,
        use_sudo=True, backup='.bak', flags='')
    sed('/etc/nginx/sites-available/%s' % project_name,
        '\{\{ssl_cert_key\}\}',
        '%s' % ssl_cert_key,
        use_sudo=True, backup='.bak', flags='')
    util.done()
