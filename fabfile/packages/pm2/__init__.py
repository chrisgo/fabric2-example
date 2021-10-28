import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Installs PM2

https://pm2.io/doc/en/runtime/overview/
"""
def install(c):
    """
    This installs PM2 only.
    Use the nodejs package to install node and npm first
    """
    util.start()
    print('Installing PM2')
    c.sudo('npm install pm2 -g')
    c.run_with_cd('~', 'pm2 install pm2-logrotate')
    c.run_with_cd('~', "pm2 set pm2-logrotate:rotateInterval '0 0 * * *'")
    print('Done Installing pm2')
    util.done()

"""
Configure
"""
def configure(c):
    util.start()
    print('Configuring PM2 ...')
    #print('Setting a new global root for npm (node_modules) to not require sudo')
    print("Installing startup script for PM2")
    c.put_template('etc-init.d-pm2', '/etc/init.d/pm2', sudo=True)
    c.sudo('chown root:root /etc/init.d/pm2')
    c.sudo('chmod +x /etc/init.d/pm2')
    print("... done installing startup script for PM2")
    c.sudo('/etc/init.d/pm2 restart')
    print('Done configuring PM2')
    util.done()

"""
Adds nginx proxy in front of node servers
Copied from lib/nginx.py add_host()
TODO: Clean this up to make it more dynamic.
      For now this is very hardcoded to the node projects inside
      the nginx-nodejs-ssl that will be placed in
      /etc/nginx/sites-available/nodejs
"""
def nginx_proxy(c):
    util.start()
    provider = c.config.provider
    project_name = c.config.project.name.lower()
    server_names = c.config.get("server_names")[env.server_role]
    server_name = server_names[0]
    # Make changes to nginx-nodejs-ssl to add more projects and ports
    c.put_template('nginx-nodejs-ssl', '/etc/nginx/sites-available/nodejs', sudo=True)
    # Merge server names
    #nginx_server_name = host_string
    print("Setting nginx server_name: %s" % server_name)
    c.sed('/etc/nginx/sites-available/nodejs', '{{localhost}}', c.host, sudo=True)
    # Deal with SSL
    ssl_cert = f'/etc/letsencrypt/live/{server_name}/fullchain.pem'
    ssl_cert_key = f'/etc/letsencrypt/live/{server_name}/privkey.pem'
    c.sed('/etc/nginx/sites-available/nodejs', '{{ssl_cert}}', ssl_cert, sudo=True)
    c.sed('/etc/nginx/sites-available/nodejs', '{{ssl_cert_key}}', ssl_cert_key, sudo=True)
    if not c.exists('/etc/nginx/sites-enabled/nodejs'):
        c.sudo('ln -s /etc/nginx/sites-available/nodejs /etc/nginx/sites-enabled/nodejs')
    #c.sudo('/etc/init.d/nginx restart')
    util.done()
