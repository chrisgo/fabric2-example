import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
PHP 7.X
As of 12/8/2019, Debian 10 installs 7.3
"""

def install(c):
    util.start()
    print('Installing PHP 7.3.x ...')
    # Install the normal stuff
    c.sudo('apt-get install -yq php-cli php-fpm')
    c.sudo('apt-get install -yq php-mysql php-curl php-gd php-xml php-zip')
    c.sudo('apt-get install -yq php-apcu php-intl php-soap php-bcmath')
    c.sudo('apt-get install -yq php-mbstring')
    print('Installing Mcrypt (no longer installed by default) ...')
    # https://gist.github.com/arzzen/1209aa4a430bd95db3090a3399e6c35f
    c.sudo('apt-get install -yq gcc make autoconf libc-dev pkg-config')
    c.sudo('apt-get install -yq gcc make autoconf libmcrypt-dev')
    c.sudo('apt-get install -yq php-pear php-dev')
    # Install Mcrypt
    if not c.exists('/usr/lib/php/20180731/mcrypt.so'):
        print('Installing Mcrypt Extension ...')
        c.sudo('echo "" | pecl install mcrypt-1.0.3')
        c.sudo('bash -c "echo extension=/usr/lib/php/20180731/mcrypt.so > /etc/php/7.3/mods-available/mcrypt.ini"')
        c.sudo('ln -s /etc/php/7.3/mods-available/mcrypt.ini /etc/php/7.3/fpm/conf.d/30-mcrypt.ini')
        c.sudo('ln -s /etc/php/7.3/mods-available/mcrypt.ini /etc/php/7.3/cli/conf.d/30-mcrypt.ini')
    else:
        print('Found existing Mcrypt Extension ...')
    # Install Redis
    if not c.exists('/usr/lib/php/20180731/redis.so'):
        print('Installing Redis Extension ...')
        c.sudo('echo "" | pecl install redis')
        c.sudo('bash -c "echo extension=/usr/lib/php/20180731/redis.so > /etc/php/7.3/mods-available/redis.ini"')
        c.sudo('ln -s /etc/php/7.3/mods-available/redis.ini /etc/php/7.3/fpm/conf.d/30-redis.ini')
        c.sudo('ln -s /etc/php/7.3/mods-available/redis.ini /etc/php/7.3/cli/conf.d/30-redis.ini')
    else:
        print('Found existing Redis Extension ...')
    c.sudo('/etc/init.d/php7.3-fpm restart')
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
        if c.exists('/etc/php/7.3/fpm/conf.d/php-custom.ini'):
            c.sudo('rm /etc/php/7.3/fpm/conf.d/php-custom.ini')
    c.put_template('php-fpm-custom.ini', '/etc/php/7.3/fpm/conf.d/php-custom.ini', sudo=True)
    # http://stackoverflow.com/questions/23443398/nginx-error-connect-to-php5-fpm-sock-failed-13-permission-denied
    # c.put_template('fpm_pool_www.conf', '/etc/php7/fpm/pool.d/www.conf', sudo=True)
    # Reload php-fpm
    c.sudo('/etc/init.d/php7.3-fpm restart')
    # 01/21/20 CG: We also have to enable mysqli.allow_local_infile = On
    # https://stackoverflow.com/questions/55818568/load-data-local-infile-forbidden-after-php-mariadb-update
    if c.exists('/etc/nginx/conf.d/php.conf'):
        if c.exists('/etc/php/7.3/cli/conf.d/php-custom.ini'):
            c.sudo('rm /etc/php/7.3/cli/conf.d/php-custom.ini')
    c.put_template('php-cli-custom.ini', '/etc/php/7.3/cli/conf.d/php-custom.ini', sudo=True)
    util.done()
