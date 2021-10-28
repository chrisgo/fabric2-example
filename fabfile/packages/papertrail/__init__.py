import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Papertrail
"""

def install(c):
    util.start()
    if not c.enabled('papertrail'):
        util.done('Not enabled in environment settings')
        return
    if c.config.papertrail.url == '':
        util.done('Missing Papertrail URL')
        return
    #papertrail_url = papertrail['url']
    #c.sudo('echo "*.*          @%s" >> /etc/rsyslog.conf' % papertrail_url)
    #c.sudo('sudo /etc/init.d/rsyslog restart')
    # Download remote syslog package
    c.run_with_cd('~', 'wget https://github.com/papertrail/remote_syslog2/releases/download/v0.20/remote-syslog2_0.20_amd64.deb')
    c.sudo_with_cd('~', f'dpkg -i /home/{c.config.project.name}/remote-syslog2_0.20_amd64.deb')
    util.done()


def configure(c):
    util.start()
    c.put_template('etc-log_files.yml', '/etc/log_files.yml', sudo=True)
    c.sed('/etc/log_files.yml', '{{port}}', c.config.papertrail.port, sudo=True)
    c.sudo("/etc/init.d/remote_syslog start")
    util.done()
