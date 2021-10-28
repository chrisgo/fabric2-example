import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Redis

Replication
https://community.pivotal.io/s/article/How-to-setup-Redis-master-and-slave-replication

As of 10/7/2019 for Debian 10
Redis server installed is 5.0.3 (Debian 9 only got to 3.x)

"""

def install(c):
    util.start()
    # If Redis host is not specified, that means we will run a local one
    if (c.config.redis.host and c.config.redis.host != ''):
        print("Not installing Redis ...")
        print(f'Using Redis @ {c.config.redis.host}:{c.config.redis.port}')
    else:
        print("Installing Redis ...")
        c.sudo('apt-get install -yq redis-server')
        # Secure Redis http://redis.io/topics/security
        search = '# requirepass foobared'
        replace = f'# requirepass foobared\\nrequirepass {c.config.project.password}'
        util.sed(c, '/etc/redis/redis.conf', search, replace, sudo=True)
        # Open redis to all IPs
        search = 'bind 127.0.0.1'
        replace = '#bind 127.0.0.1\\nbind 0.0.0.0'
        util.sed(c, '/etc/redis/redis.conf', search, replace, sudo=True)
        # Restart redis
        c.sudo('/etc/init.d/redis-server restart')
    util.done()


def configure(c):
    util.start()
    #
    # Additionally, for extra security, we can use IP tables
    #
    # Comment out the bind
    #sed('/etc/redis/redis.conf', 'bind 127.0.0.1', '#bind 127.0.0.1', use_sudo=True)
    # Restart redis
    #sudo('/etc/init.d/redis-server restart')
    # Setup IP tables
    # Block Redis port (6379) and resque-web port (5678)
    #sudo('iptables -A INPUT -j DROP -p tcp --destination-port 6379 -i eth0')
    #sudo('iptables -A INPUT -j DROP -p tcp --destination-port 5678 -i eth0')
    # IPs for dev computers
    ips = ['68.111.83.216', '198.15.79.146']
    # IPs for Linode servers
    ips.extend(['173.255.196.166', '173.230.148.249', '173.255.255.61'])
    # IPs for Uptimerobot
    ips.extend(['74.86.158.106', '74.86.158.107', '74.86.179.130'])
    ips.extend(['74.86.179.131', '46.137.190.132', '122.248.234.23'])
    # Add back the IPs
    #for ip in ips:
    #   sudo('iptables -I INPUT -s %s -j ACCEPT' % ip)
    # Restart redis
    sudo('/etc/init.d/redis-server restart')
    util.done()

"""
Make one server a slave to master
https://www.digitalocean.com/community/tutorials/how-to-configure-a-redis-cluster-on-ubuntu-14-04
"""
def slave(c):
    util.start()
    # Edit redis.conf
    #slaveof your_redis_master_ip 6379
    #masterauth your_redis_master_password
    #sudo('/etc/init.d/redis-server restart')
    util.end()
