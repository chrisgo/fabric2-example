import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
PHP 8.X
As of 2/1/21 Debian 10 "buster" installs 7.3
So we need to alternative instructions
https://www.cloudbooklet.com/how-to-install-php-8-on-debian/
https://computingforgeeks.com/how-to-install-php-on-debian-linux/
"""

def install(c):
    util.start()
    print('Installing PHP 8.x ...')
    # (1) We have to add the packages.sury.org repo to APT
    c.sudo('apt -y install lsb-release apt-transport-https ca-certificates wget')
    c.sudo('wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg')
    # (2) Add the repos to the apt sources list
    if not c.exists('/etc/apt/sources.list.d/sury-php8.list'):
        c.put_template('sury-php8.list', '/etc/apt/sources.list.d/sury-php8.list', sudo=True)
    # (3) APT Update
    c.sudo('apt-get update')
    # (4) APT install
    c.sudo('apt-get install -yq php8.0')
    c.sudo('apt-get install -yq php8.0-cli php8.0-fpm')
    c.sudo('apt-get install -yq php8.0-mysql php8.0-curl php8.0-gd php8.0-xml php8.0-zip')
    c.sudo('apt-get install -yq php8.0-apcu php8.0-intl php8.0-soap php8.0-bcmath')
    c.sudo('apt-get install -yq php8.0-mbstring')
    # (5) Install the DEV tools for extensions that we have to build manually
    c.sudo('apt-get install -yq gcc make autoconf libc-dev pkg-config')
    c.sudo('apt-get install -yq gcc make autoconf libmcrypt-dev')
    c.sudo('apt-get install -yq php-pear')
    c.sudo('apt-get install -yq php8.0-dev')
    # (6) Mcrypt
    #print('Installing Mcrypt (no longer installed by default) ...')
    #if not c.exists('/usr/lib/php/20200930/mcrypt.so'):
    #    print('Installing Mcrypt Extension ...')
    #    c.sudo('echo "" | pecl install mcrypt-1.0.4')
    #    c.sudo('bash -c "echo extension=/usr/lib/php/20200930/mcrypt.so > /etc/php/8.0/mods-available/mcrypt.ini"')
    #    c.sudo('ln -s /etc/php/8.0/mods-available/mcrypt.ini /etc/php/8.0/fpm/conf.d/30-mcrypt.ini')
    #    c.sudo('ln -s /etc/php/8.0/mods-available/mcrypt.ini /etc/php/8.0/cli/conf.d/30-mcrypt.ini')
    #else:
    #    print('Found existing Mcrypt Extension ...')
    # (7) Install Redis
    if not c.exists('/usr/lib/php/20200930/redis.so'):
        print('Installing Redis Extension (currently 5.3.3) ...')
        #c.sudo('echo "" | pecl install redis')
        c.sudo('pecl install redis')
        c.sudo('bash -c "echo extension=/usr/lib/php/20200930/redis.so > /etc/php/8.0/mods-available/redis.ini"')
        c.sudo('ln -s /etc/php/8.0/mods-available/redis.ini /etc/php/8.0/fpm/conf.d/30-redis.ini')
        c.sudo('ln -s /etc/php/8.0/mods-available/redis.ini /etc/php/8.0/cli/conf.d/30-redis.ini')
    else:
        print('Found existing Redis Extension ...')
    c.sudo('/etc/init.d/php8.0-fpm restart')
    util.done()


def configure(c):
    util.start()
    # Enable php for nginx
    print('Routing .php from nginx to php-fpm')
    if c.exists('/etc/nginx/conf.d/php.conf'):
        c.sudo('rm /etc/nginx/conf.d/php.conf')
    c.put_template('php.conf', '/etc/nginx/conf.d/php.conf', sudo=True)
    # Add custom php.ini settings
    print('Adding custom php.ini settings')
    if c.exists('/etc/nginx/conf.d/php.conf'):
        if c.exists('/etc/php/8.0/fpm/conf.d/php-custom.ini'):
            c.sudo('rm /etc/php/8.0/fpm/conf.d/php-custom.ini')
    c.put_template('php-fpm-custom.ini', '/etc/php/8.0/fpm/conf.d/php-custom.ini', sudo=True)
    # http://stackoverflow.com/questions/23443398/nginx-error-connect-to-php5-fpm-sock-failed-13-permission-denied
    # c.put_template('fpm_pool_www.conf', '/etc/php7/fpm/pool.d/www.conf', sudo=True)
    # Reload php-fpm
    c.sudo('/etc/init.d/php8.0-fpm restart')
    # 01/21/20 CG: We also have to enable mysqli.allow_local_infile = On
    # https://stackoverflow.com/questions/55818568/load-data-local-infile-forbidden-after-php-mariadb-update
    if c.exists('/etc/nginx/conf.d/php.conf'):
        if c.exists('/etc/php/8.0/cli/conf.d/php-custom.ini'):
            c.sudo('rm /etc/php/8.0/cli/conf.d/php-custom.ini')
    c.put_template('php-cli-custom.ini', '/etc/php/8.0/cli/conf.d/php-custom.ini', sudo=True)
    util.done()
