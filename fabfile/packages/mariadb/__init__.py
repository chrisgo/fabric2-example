import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from pipes import quote
from fabfile.core import *

#from fabfile.packages import automysqlbackup
#from random import randint

"""
MariaDB
As of 9/24/17 Debian 8.x "jessie" (8.9 to be specific)
Version: Server version: 10.1.26-MariaDB-1~jessie mariadb.org binary distribution

As of 12/7/2019 Debian 10.x "buster" will install 10.3.x (1:10.3.18-0+deb10u1: all)

"""

def install(c):
    util.start()
    # Install mariadb-server (10.1.37-MariaDB-0+deb9u1 Debian 9.6)
    c.sudo('apt-get install -yq mariadb-server')
    c.sudo('apt-get install -yq mariadb-backup')
    # Update root password
    # 10/26/21 CG: As of mariadb 10.4+, the UPDATE user does not work anymore
    # ALTER USER root@localhost IDENTIFIED VIA mysql_native_password;
    #query = f"SET PASSWORD FOR 'root'@'localhost' = PASSWORD('{c.config.project.password}'); " \
    #        "UPDATE mysql.user SET plugin = '' WHERE user = 'root' AND host = 'localhost'; " \
    #        "FLUSH PRIVILEGES; "
    query = f"SET PASSWORD FOR 'root'@'localhost' = PASSWORD('{c.config.project.password}'); " \
            "ALTER USER root@localhost IDENTIFIED VIA mysql_native_password; " \
            "FLUSH PRIVILEGES; "
    c.sudo(f'mysql -u root --execute="{query}"');
    # Load timezone info
    c.run(f'mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql --user=root --password={c.config.project.password} mysql')
    # Restart
    c.sudo('/etc/init.d/mariadb restart')
    util.done()


def configure(c):
    util.start()
    # Configure
    # 1/24/19 CG: File is now at /etc/mysql/mariadb.conf.d/50-server.cnf
    #config = '/etc/mysql/my.cnf';
    config = '/etc/mysql/mariadb.conf.d/50-server.cnf';
    c.sed(config, '127.0.0.1', '0.0.0.0', sudo=True)
    # Get the innodb config file up to the server
    if (c.is_production()):
        # Check if innodb.cnf already exists
        print("Copying innodb.cnf ...")
        if c.exists('/etc/mysql/mariadb.conf.d/60-innodb.cnf'):
            c.sudo('rm -fR /etc/mysql/mariadb.conf.d/60-innodb.cnf')
        c.put_template('innodb.cnf', '/etc/mysql/mariadb.conf.d/60-innodb.cnf', sudo=True)
        print("Copying replication.cnf ...")
        if c.exists('/etc/mysql/mariadb.conf.d/60-replication.cnf'):
            c.sudo('rm -fR /etc/mysql/mariadb.conf.d/60-replication.cnf')
        c.put_template('replication.cnf', '/etc/mysql/mariadb.conf.d/60-replication.cnf', sudo=True)
        # TODO: Use the index of this slave server
        # For example, if host is prd-mdb7.{_project_name}.com, use "7" as the server_id
        #server_id = randint(100, 999)
        server_id = int(filter(str.isdigit, c.host))
        print(f'Setting server_id: {server_id}')
        c.sed('/etc/mysql/mariadb.conf.d/60-replication.cnf', '{{server_id}}', server_id, sudo=True)
    # Restart
    c.sudo('/etc/init.d/mysql restart')
    util.done()

"""
Master
"""
def configure_master(c):
    """
    Configure master
    """
    util.start()
    # Create replication user
    # TODO: Make this more restrictive so specify server ip of slaves
    # TODO: Make the password something else instead of the root password
    # GRANT REPLICATION SLAVE ON *.* TO 'replication_user'@'<slave-server-ip>' IDENTIFIED BY '<password>';
    query = "GRANT REPLICATION SLAVE ON *.* TO " \
            f"'replication_user'@'%' IDENTIFIED BY '{c.config.project.password}' WITH GRANT OPTION;"
    c.run(f'mysql --batch --raw --skip-column-names --user={c.config.project.username} --password={c.config.project.password} --execute="{query}"')
    c.sudo('/etc/init.d/mysql restart')
    util.done()

"""
Slave
"""
def configure_slave(c):
    """
    Configure slave
    """
    util.start()
    # c.sudo('/etc/init.d/mysql restart')
    # Other things have to be done manually
    #
    # sudo cat /var/lib/mysql/xtrabackup_binlog_info
    #
    # Example output (note the last number with the dashes, this is the GTID position)
    # mariadb-bin.000096 568 0-1-2
    #
    # mysql > SET GLOBAL gtid_slave_pos = "0-1-2";  # from master server
    # mysql > CHANGE MASTER TO master_host="<master-server-ip>",
    #                           master_user="replication_user",
    #                           master_password="<password>",
    #                           master_port=3306,
    #                           master_use_gtid=slave_pos;
    # mysql > START SLAVE;
    # mysql > SHOW SLAVE STATUS \G;
    #
    # check "status" => waiting for master and "seconds behind master" => 0
    #
    util.done()

"""
Backup
"""
def configure_backup(c):
    """
    Configure backup systems
    Currently using: automysqlbackup to s3fs mount
    """
    util.start()
    #xtrabackup.install()
    #xtrabackup.configure()
    automysqlbackup.install(c)
    automysqlbackup.configure(c)
    util.done()
