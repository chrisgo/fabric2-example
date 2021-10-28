import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from fabfile.core import *

"""
Installs requirements to run Puppeteer

- xvfb (X virtual framebuffer)
- supervisor

Then to run puppet:

DEBUG=puppeteer xvfb-run --server-args="-screen 0 1024x768x24" node cnn.js
"""
def install(c):
    util.start()
    print('Start Puppeteer Stack ...')
    print('Installing xvfb ...')
    c.sudo('apt-get install -yq xvfb x11-xkb-utils clang')
    c.sudo('apt-get install -yq xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps')
    c.sudo('apt-get install -yq libdbus-1-dev libgtk2.0-dev libnotify-dev libgnome-keyring-dev')
    c.sudo('apt-get install -yq libgconf2-dev libasound2-dev libcap-dev libcups2-dev libxtst-dev')
    c.sudo('apt-get install -yq libxss1 libnss3-dev gcc-multilib g++-multilib')
    print("Installing Supervisor ...")
    # https://laravel.com/docs/5.7/queues#supervisor-configuration
    c.sudo('apt-get install -yq supervisor')
    util.done()

"""
Configure
"""
def configure(c):
    util.start()
    print('Configuring xvfb ...')
    print('Copying startup script for xvfb ...')
    c.put_template('etc-init.d-xvfb.sh', '/etc/init.d/xvfb', sudo=True)
    c.sudo('chmod +x /etc/init.d/xvfb')
    c.sudo('sudo update-rc.d xvfb defaults')
    print('Starting xvfb ...')
    c.sudo('/etc/init.d/xvfb start')
    print('Done configuring xvfb')
    print('Configuring supervisor ...')
    c.put_template('supervisor-puppeteer.conf', '/etc/supervisor/conf.d/puppeteer.conf', sudo=True)
    #sudo('supervisorctl reread')
    #sudo('supervisorctl update')
    #sudo('supervisorctl start puppeteer-elliemae:*')
    print('Done configuring supervisor')
    util.done()
