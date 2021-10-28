import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Elasticsearch http://elastic.io

As of 9/4/2016, version is 2.1.2

https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-repositories.html

"""

def install(c):
    util.start()
    # Get the public key
    c.run('wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -')
    # Create an apt source record
    #c.run('echo "deb https://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list')
    #c.sudo('apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db')
    c.put_template('etc-apt-elasticsearch.list', '/etc/apt/sources.list.d/elasticsearch.list', sudo=True)
    c.sudo('apt-get install -yq nginx')
    c.sudo('apt-get install -yq openjdk-7-java')
    # Also install JDK8
    c.put_template('etc-apt-java8.list', '/etc/apt/sources.list.d/java8.list', sudo=True)
    c.sudo('apt-get update')
    c.sudo('apt-get install openjdk-8-jdk')
    c.sudo('update-alternatives --config java')
    #if not exists('mkdir /usr/java'):
    #    c.sudo('mkdir /usr/java')
    #c.sudo('ln -s /usr/lib/jvm/java-7-openjdk-amd64 /usr/java/default')
    c.sudo('apt-get install -yq elasticsearch')
    util.done()

def configure(c):
    util.start()
    # Start automatically
    c.sudo('update-rc.d elasticsearch defaults 95 10')
    c.sudo('/bin/systemctl daemon-reload')
    c.sudo('/bin/systemctl enable elasticsearch.service')
    # Create nginx site
    c.put_template('.htpasswd', '/var/www/.htpasswd', sudo=True)
    c.put_template('nginx-site-elasticsearch', '/etc/nginx/sites-available/elasticsearch', sudo=True)
    c.sudo_with_cd('/etc/nginx/sites-enabled', 'ln -s ../sites-available/elasticsearch elasticsearch')
    c.sudo('/etc/init.d/nginx restart')
    util.done()
