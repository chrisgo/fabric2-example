import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Installs NodeJS (and npm)

https://github.com/nodesource/distributions#debinstall
Need to do this so that npm install does NOT need root
http://www.sitepoint.com/beginners-guide-node-package-manager/

"""

def install(c):
    """
    This install NodeJS only
    """
    #install_node4():
    #install_node5():
    #install_node6();
    #install_node10(c);
    #install_node12(c);
    install_node14(c);

"""
Stable as of 4/21/2020 is 14.x
"""
def install_node14(c):
    """
    Installs NodeJS 14.x Stable (LTS as of Oct 2020)
    """
    util.start()
    print('Installing NodeJS 14.x')
    c.sudo('curl -sL https://deb.nodesource.com/setup_14.x | bash -')
    c.sudo('apt-get install -yq nodejs')
    c.sudo('apt-get install -yq build-essential')
    print('Done Installing Nodejs')
    c.run('node -v')
    # Upgrade npm
    c.sudo('npm install npm -g')
    print('Done Upgrading npm')
    c.run('npm -v')
    util.done()

"""
Stable as of 4/23/2019 is 12.x
"""
def install_node12(c):
    """
    Installs NodeJS 12.x Stable (LTS as of Oct 2020)
    """
    util.start()
    print('Installing NodeJS 12.x')
    c.sudo('curl -sL https://deb.nodesource.com/setup_12.x | bash -')
    c.sudo('apt-get install -yq nodejs')
    c.sudo('apt-get install -yq build-essential')
    print('Done Installing Nodejs')
    c.run('node -v')
    # Upgrade npm
    c.sudo('npm install npm -g')
    print('Done Upgrading npm')
    c.run('npm -v')
    util.done()

"""
Stable as of 12/05/18 is 10.x
"""
def install_node10(c):
    """
    Installs NodeJS 10.x Stable (LTS as of Dec 2018)
    """
    util.start()
    print('Installing NodeJS 10.x')
    c.sudo('curl -sL https://deb.nodesource.com/setup_10.x | bash -')
    c.sudo('apt-get install -yq nodejs')
    c.sudo('apt-get install -yq build-essential')
    print('Done Installing Nodejs')
    c.run('node -v')
    # Upgrade npm
    c.sudo('npm install npm -g')
    print('Done Upgrading npm')
    c.run('npm -v')
    util.done()

"""
Configure
"""
def configure(c):
    util.start()
    print('Configuring Nodejs ...')
    print('Done configuring Nodejs')
    util.done()

"""
LTS is 4x
"""
def install_node4():
    """
    Installs NodeJS 4.x LTS
    """
    util.start()
    print('Installing NodeJS 4.x')
    c.sudo('curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -')
    c.sudo('apt-get install -yq nodejs')
    c.sudo('apt-get install -yq build-essential')
    print('Done Installing Nodejs')
    c.run('node -v')
    # Upgrade npm
    c.sudo('npm install npm -g')
    print('Done Upgrading npm')
    c.run('npm -v')
    c.sudo('npm install pm2 -g')
    print('Done Installing pm2')
    util.done()

"""
Not supported
"""
def install_node5():
    """
    Install NodeJs 5.x
    """
    util.start()
    print('Installing NodeJS 5.x')
    c.sudo('curl -sL https://deb.nodesource.com/setup_5.x | sudo bash -')
    #print('Installing NodeJS 4.x LTS (latest is 5.x)')
    #c.sudo('curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -')
    c.sudo('apt-get install -yq nodejs')
    c.sudo('apt-get install -yq build-essential')
    # We want to get npm to use another global that is not sudo required
    # http://www.sitepoint.com/beginners-guide-node-package-manager/
    print('Done Installing Nodejs')
    c.run('node -v')
    # Upgrade npm
    c.sudo('npm install npm -g')
    print('Done Upgrading npm')
    c.run('npm -v')
    c.sudo('npm install pm2 -g')
    print('Done Installing pm2')
    util.done()

"""
Stable as of 9/4/2016 is 6x
"""
def install_node6():
    """
    Installs NodeJS 6.x Stable
    """
    util.start()
    print('Installing NodeJS 6.x')
    c.sudo('curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -')
    c.sudo('apt-get install -yq nodejs')
    c.sudo('apt-get install -yq build-essential')
    print('Done Installing Nodejs')
    c.run('node -v')
    # Upgrade npm
    c.sudo('npm install npm -g')
    print('Done Upgrading npm')
    c.run('npm -v')
    c.sudo('npm install pm2 -g')
    c.run_with_cd('~', 'pm2 install pm2-logrotate')
    c.run_with_cd('~', "pm2 set pm2-logrotate:rotateInterval '0 0 * * *'")
    print('Done Installing pm2')
    util.done()
