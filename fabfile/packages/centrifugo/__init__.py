import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Centrifugo Websocket Server written in Go
https://centrifugal.github.io/centrifugo/server/install/

For now, we are going to try to install using the DEB packages
published in https://packagecloud.io/
"""

def install(c):
    util.start()
    # (1) Get the apt-key
    c.run('wget -O - https://packagecloud.io/FZambia/centrifugo/gpgkey | sudo apt-key add -')
    # (2) Set the apt list
    if not c.exists('/etc/apt/sources.list.d/centrifugo.list'):
        c.put_template('newrelic.list', '/etc/apt/sources.list.d/centrifugo.list', sudo=True)
    c.sudo('apt-get update')
    # (3) Install
    c.sudo('apt-get install -yq centrifugo')
    # (4) Copy the start up script
    if not c.exists('/etc/init.d/centrifugo'):
        c.put_template('etc_init_centrifugo', '/etc/init.d/centrifugo', sudo=True)
        c.sudo('chmod +x /etc/init.d/centrifugo')
    # (5) Open up port 8000 to private IP
    c.sudo('ufw allow in on eth1 to any port 8000')
    #sudo('ufw --force enable')
    util.done()


def configure(c):
    util.start()
    # (1) Get some vars
    project_name = env.project_name.lower()
    # (2) Update the config file
    if not c.exists('/etc/centrifugo'):
        c.sudo('mkdir /etc/centrifugo')
    if not c.exists('/etc/centrifugo/config.json'):
        c.put_template('config.json', '/etc/centrifugo/config.json', sudo=True)
    # (2.1) Replace token
    c.sed('/etc/centrifugo/config.json', '{{password}}', c.config.project.password, sudo=True)
    # (3) Restart the centrifugo with new config
    c.sudo('/etc/init.d/centrifugo restart')
    # (4) Add nginx virtual host
    print('Adding new virtual host')
    # (4.1) Delete old virtual host file
    if c.exists('/etc/nginx/sites-available/centrifugo'):
        c.sudo('rm /etc/nginx/sites-available/centrifugo')
        print('Found old virtual host, archiving')
    # (4.2) Copy new virtual host
    c.put_template('centrifugo.nginx', '/etc/nginx/sites-available/centrifugo', sudo=True)
    # (4.3) Do the token replacements
    search = '{{localhost}}'
    replace = '%s' % " ".join(server_names)
    c.sed(f'/etc/nginx/sites-available/{c.config.project.name}', search, replace, sudo=True)
    # (4.4) SSL Certificate
    ssl_cert = f'/etc/letsencrypt/live/{c.config.project.name}.com/fullchain.pem'
    ssl_cert_key = f'/etc/letsencrypt/live/{c.config.project.name}.com/privkey.pem'
    # (4.5) Replace token
    c.sed(f'/etc/nginx/sites-available/{c.config.project.name}', '{{ssl_cert}}', ssl_cert, sudo=True)
    c.sed(f'/etc/nginx/sites-available/{c.config.project.name}', '{{ssl_cert_key}}', ssl_cert_key, sudo=True)
    # (4.6) Link to sites-enabled
    if not c.exists('/etc/nginx/sites-enabled/centrifugo'):
        c.sudo_with_cd('/etc/nginx/sites-enabled', 'ln -s ../sites-available/centrifugo centrifugo')
    # (4.7) Restart nginx
    c.sudo('/etc/init.d/nginx restart')
    util.done()
