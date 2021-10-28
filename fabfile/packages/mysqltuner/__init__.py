import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Mysqltuner
https://github.com/major/MySQLTuner-perl

Once this is installed, we run it via the following command

ssh {_project_name}@prd-mdb1.{_project_name}.com
cd ~/tmp
perl ./mysqltuner.pl --outputfile /mnt/s3fs/database/mysqltuner/prd-mdb1.{_project_name}.com

"""

def install(c):
    util.start()
    if not c.exists('~/tmp'):
        c.run('mkdir ~/tmp')
    c.run_with_cd('~/tmp', 'wget http://mysqltuner.pl/ -O mysqltuner.pl')
    c.run_with_cd('~/tmp', 'wget https://raw.githubusercontent.com/major/MySQLTuner-perl/master/basic_passwords.txt -O basic_passwords.txt')
    c.run_with_cd('~/tmp', 'wget https://raw.githubusercontent.com/major/MySQLTuner-perl/master/vulnerabilities.csv -O vulnerabilities.csv')
    c.run_with_cd('~/tmp', 'chmod +x mysqltuner.pl')
    util.done()


def configure(c):
    util.start()
    util.done()
