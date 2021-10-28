import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
PHP (default) on Debian 11 (bullseye)
As of 10/25/21 Debian 10 "buster" installs 7.4
Module Directory for 7.4 => /usr/lib/php/20190902
"""

VERSION = '7.4'
MODULE_DIR = '20190902'

def install(c):
    util.start()
    print('Installing PHP (default on debian 11 is 7.4.x)...')
    _version = c.config.php.version
    _api_version = c.config.php.api_version
    c.sudo('apt-get update')
    # (4) APT install
    c.sudo('apt-get install -yq php')
    c.sudo('apt-get install -yq php-cli php-fpm')
    c.sudo('apt-get install -yq php-mysql php-curl php-gd php-xml php-zip')
    c.sudo('apt-get install -yq php-apcu php-intl php-soap php-bcmath')
    c.sudo('apt-get install -yq php-mbstring')
    # (5) Install the DEV tools for extensions that we have to build manually
    c.sudo('apt-get install -yq gcc make autoconf libc-dev pkg-config')
    c.sudo('apt-get install -yq gcc make autoconf libmcrypt-dev')
    c.sudo('apt-get install -yq php-pear')
    c.sudo('apt-get install -yq php-dev')
    # (6) Mcrypt
    print('Installing Mcrypt (no longer installed by default) ...')
    if not c.exists(f'/usr/lib/php/{_api_version}/mcrypt.so'):
        print('Installing Mcrypt Extension ...')
        c.sudo('pecl channel-update pecl.php.net')
        c.run('echo "" | sudo pecl install mcrypt-1.0.4')
        c.sudo(f'bash -c "echo extension=/usr/lib/php/{_api_version}/mcrypt.so > /etc/php/{_version}/mods-available/mcrypt.ini"')
        c.sudo(f'ln -s /etc/php/{_version}/mods-available/mcrypt.ini /etc/php/{_version}/fpm/conf.d/30-mcrypt.ini')
        c.sudo(f'ln -s /etc/php/{_version}/mods-available/mcrypt.ini /etc/php/{_version}/cli/conf.d/30-mcrypt.ini')
    else:
        print('Found existing Mcrypt Extension ...')
    # (7) Install Redis
    if not c.exists(f'/usr/lib/php/{_api_version}/redis.so'):
        print('Installing Redis Extension (currently 5.3.3) ...')
        #c.sudo('echo "" | pecl install redis')
        c.sudo('pecl install redis')
        c.sudo(f'bash -c "echo extension=/usr/lib/php/{_version}/redis.so > /etc/php/{_version}/mods-available/redis.ini"')
        c.sudo(f'ln -s /etc/php/{_version}/mods-available/redis.ini /etc/php/{_version}/fpm/conf.d/30-redis.ini')
        c.sudo(f'ln -s /etc/php/{_version}/mods-available/redis.ini /etc/php/{_version}/cli/conf.d/30-redis.ini')
    else:
        print('Found existing Redis Extension ...')
    c.sudo(f'/etc/init.d/php{_version}-fpm restart')
    util.done()

def configure(c):
    util.start()
    _version = c.config.php.version
    # Enable php for nginx
    print('Routing .php from nginx to php-fpm')
    if c.exists('/etc/nginx/conf.d/php.conf'):
        c.sudo('rm /etc/nginx/conf.d/php.conf')
    c.put_template('php.conf', '/etc/nginx/conf.d/php.conf', sudo=True)
    # Add custom php.ini settings
    print('Adding custom php.ini settings')
    if c.exists('/etc/nginx/conf.d/php.conf'):
        if c.exists(f'/etc/php/{_version}/fpm/conf.d/php-custom.ini'):
            c.sudo(f'rm /etc/php/{_version}/fpm/conf.d/php-custom.ini')
    c.put_template('php-fpm-custom.ini', f'/etc/php/{_version}/fpm/conf.d/php-custom.ini', sudo=True)
    # http://stackoverflow.com/questions/23443398/nginx-error-connect-to-php5-fpm-sock-failed-13-permission-denied
    # c.put_template('fpm_pool_www.conf', '/etc/php7/fpm/pool.d/www.conf', sudo=True)
    # Reload php-fpm
    c.sudo(f'/etc/init.d/php{_version}-fpm restart')
    # 01/21/20 CG: We also have to enable mysqli.allow_local_infile = On
    # https://stackoverflow.com/questions/55818568/load-data-local-infile-forbidden-after-php-mariadb-update
    if c.exists('/etc/nginx/conf.d/php.conf'):
        if c.exists(f'/etc/php/{_version}/cli/conf.d/php-custom.ini'):
            c.sudo(f'rm /etc/php/{_version}/cli/conf.d/php-custom.ini')
    c.put_template('php-cli-custom.ini', f'/etc/php/{_version}/cli/conf.d/php-custom.ini', sudo=True)
    util.done()
