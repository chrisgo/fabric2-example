import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
S3FS

sudo s3fs s3fs-test.{_project_name}.com /mnt/s3fs-test -o allow_other -o passwd_file=/etc/passwd-s3fs -d -d -f -o f2 -o curldbg

10/27/18 CG: CPU spikes and high cost (ListBucket and HEAD calls)
https://gitlab.com/{_project_name}/main/issues/81
locate and updatedb scans local file systems "daily" which causes high usage
and probably overscans the mount point causing lots of hits to Amazon S3 servers
http://linux-sxs.org/utilities/updatedb.html
So we added /mnt/s3fs to /etc/updatedb.conf to PRUNEPATHS
...
PRUNEPATHS="/tmp /var/spool /media /mnt/s3fs"
...
01/23/19 CG: updatedb and locatedb does not seem to exist in Debian 9

4/22/20 CG: Add cronjob to delete files older than X days
S3FS documentation says it does do it by itself so we have to find another
way to clear this cache folder, otherwise it fills up and the s3 folder
fails to mount and then it causes MASSIVE problems
https://github.com/s3fs-fuse/s3fs-fuse/wiki/Fuse-Over-Amazon#details

2/7/21 CG: Add s3cmd so we can sync files between server and S3 bucket
https://medium.com/@pealami/one-of-the-best-way-for-automatic-data-backup-to-s3-using-automysqlbackup-with-s3cmd-2b20ce92dbde
https://supunkavinda.blog/mysql-backups-in-amazon-s3

"""

def install(c):
    util.start()
    if not c.enabled('s3fs'):
        util.done('Not enabled in environment settings')
        return
    #install_v161()
    #install_v184()
    install_latest(c)
    # Add cronjob to delete files older than X days
    # https://tecadmin.net/delete-files-older-x-days/
    # find /tmp/s3fs.{_project_name}.com -type f -mtime +30 -exec sudo rm {} -f \;
    c.put_template('cron_clear_cache', '/etc/cron.daily/s3fs_clear_cache', sudo=True)
    # Also install s3cmd
    c.sudo('apt-get install -yq s3cmd')
    util.done()


def install_latest(c):
    """
    We are using git clone so we are getting the "master" branch
    Last release is v1.85 (03/11/2019)
    Last release is v1.84 (07/8/2018) which is almost 6 months ago
    """
    # (1) Install some basic build tools
    c.sudo('apt-get install -yq fuse')
    c.sudo('apt-get install -yq automake autotools-dev g++ git libcurl4-gnutls-dev libfuse-dev libssl-dev libxml2-dev make pkg-config')
    # (2) Clone into a folder locally
    c.run_with_cd('~', 'rm -fR s3fs-fuse')
    c.run_with_cd('~', 'git clone https://github.com/s3fs-fuse/s3fs-fuse.git')
    # (3) Run the build
    c.run_with_cd('~/s3fs-fuse', './autogen.sh')
    c.run_with_cd('~/s3fs-fuse', './configure --prefix=/usr')
    c.run_with_cd('~/s3fs-fuse', './configure')
    c.run_with_cd('~/s3fs-fuse', 'make')
    c.run_with_cd('~/s3fs-fuse', 'sudo make install')


def configure(c):
    """
    Configure
    """
    util.start()
    if not c.enabled('s3fs'):
        util.done('Not enabled in environment settings')
        return
    print("Configuring s3cmd ...")
    s3cfg = f'/home/{c.config.project.username}/.s3cfg'
    #if exists(s3cfg):
    #    sudo('rm %s' % s3cfg)
    #c.put_template('.s3cfg', s3cfg, sudo=False)
    #sed(s3cfg, '\{\{access_key\}\}', '%s' % aws_buckets[0]['access_key'], use_sudo=False, flags='', backup='')
    #sed(s3cfg, '\{\{secret_key\}\}', '%s' % aws_buckets[0]['secret_key'], use_sudo=False, flags='', backup='')
    # bucket_location
    util.done()


def mount(c):
    """
    Mount a specific bucket to a mount point
    """
    util.start()
    # (1) Check if s3fs is enabled
    if not c.enabled('s3fs'):
        print('Not enabled in environment settings')
        return
    # (2) Make sure there is a mount point
    if not c.config.mount_root:
        print('Not mount root in environment config')
        return
    # (3) Make sure there are AWS buckets
    if not c.config.aws.buckets:
        print('Not buckets in main config')
        return
    # (4) Create the password file
    print("Mounting S3FS ...")
    if c.exists('/etc/passwd-s3fs'):
        print("Delete existing passwd file ...")
        c.sudo('rm -fR /etc/passwd-s3fs')
    print('Create s3fs passwd file')
    c.sudo('touch /etc/passwd-s3fs')
    # (4.1) Loop through each bucket (normally there is only one)
    #       and create each bucket as an entry into the password-s3fs file
    for aws_bucket in c.config.aws.buckets:
        _aws_bucket_name = aws_bucket['name']
        _aws_access_key = aws_bucket['access_key']
        _aws_secret_key = aws_bucket['secret_key']
        #c.append('/etc/passwd-s3fs', f'{aws_bucket_name}:{aws_access_key}:{aws_secret_key}', escape=False, sudo=True)
        c.append('/etc/passwd-s3fs', f'{_aws_bucket_name}:{_aws_access_key}:{_aws_secret_key}', sudo=True)
    # (4.2) Change the permissions
    c.sudo('chown root:root /etc/passwd-s3fs')
    c.sudo('chmod 400 /etc/passwd-s3fs')
    # (5) Update fstab
    print('Update fstab to automount')
    # (5.1) If this is the first ever touch, the .orig file should not exist
    if not c.exists('/etc/fstab.orig'):
        c.sudo('cp /etc/fstab /etc/fstab.orig')
    # (5.2) Backup the current fstab with timestamp as well
    c.sudo(f'cp /etc/fstab /etc/{util.timestamp('fstab')}')
    # (5.3) If the fstab.orig file exists, this means that this is NOT
    #       the first time fabric has come around so we want to copy
    #       the original
    if c.exists('/etc/fstab.orig'):
        c.sudo('rm /etc/fstab')
        c.sudo('cp /etc/fstab.orig /etc/fstab')
    for aws_bucket in c.config.aws.buckets:
        _mount_point = f'{c.config.mount_root}/{aws_bucket["mount"]}')
        print(f'Mounting bucket: {aws_bucket["name"]} => mount_point')
        c.sudo('echo "\n" >> /etc/fstab')
        # s3fs#s3fs.domain.com  /mnt/s3fs/  fuse    allow_other 0   0
        # 9/28/17 CG Need new settings for dot-style bucket names
        # 9/28/17 CG Need to specify URL
        # ,use_path_request_style,url=https://s3-us-west-1.amazonaws.com
        # If region is "us-east-1", we do not put the url
        # 9/10/18 CG: Also try 3 new options: noatime,stat_cache_expire=3600,enable_noobj_cache,
        # https://stackoverflow.com/questions/23939179/ftp-sftp-access-to-an-amazon-s3-bucket#23946418
        # http://tldp.org/LDP/solrhe/Securing-Optimizing-Linux-RH-Edition-v1.3/chap6sec73.html
        if aws_bucket['region'] == "us-east-1":
            _bucket_name = aws_bucket['name']
            _fstab = f's3fs# {_bucket_name} {_mount_point} fuse    _netdev,allow_other,use_cache=/tmp,umask=0000,use_path_request_style,ensure_diskfree=4096    0    0'
        else:
            _bucket_name = aws_bucket['name']
            _region_name = aws_bucket['region']
            _fstab = f's3fs# {_bucket_name} {_mount_point} fuse    _netdev,allow_other,use_cache=/tmp,umask=0000,use_path_request_style,ensure_diskfree=4096,url=https://s3-{_region_name}.amazonaws.com    0    0'
        c.append('/etc/passwd-s3fs', _fstab, sudo=True)
    c.sudo('mount -a')
    # 1/23/19 CG: Add the fix for excessive AWS hits
    util.done()


# ============================================================
# NOT USED
# ============================================================

def install_v184(c):
    """
    Working version 1.84
    Checked on 1/23/2019 and latest version is 1.84 (7/8/2018)
    There are 110 commits after this to master
    """
    s3fs_version = "1.84"
    c.sudo('apt-get install -yq fuse')
    c.sudo('apt-get install -yq automake autotools-dev g++ git libcurl4-gnutls-dev libfuse-dev libssl-dev libxml2-dev make pkg-config')
    c.run_with_cd('~', f'wget https://github.com/s3fs-fuse/s3fs-fuse/archive/v{s3fs_version}.tar.gz')
    c.run_with_cd('~', f'tar xzvf v{s3fs_version}.tar.gz')
    c.run_with_with_cd(f'~/s3fs-fuse-{s3fs_version}', './autogen.sh')
    c.run_with_cd(f'~/s3fs-fuse-{s3fs_version}', './configure --prefix=/usr')
    c.run_with_cd(f'~/s3fs-fuse-{s3fs_version}', './configure')
    c.run_with_cd(f'~/s3fs-fuse-{s3fs_version}', 'make')
    c.run_with_cd(f'~/s3fs-fuse-{s3fs_version}', 'sudo make install')


def install_v161(c):
    """
    Working version 1.61
    """
    s3fs_version = "1.61"
    c.sudo('apt-get install -yq libfuse2')
    #sudo('apt-get install -yq fuse-utils')
    c.sudo('apt-get install -yq fuse libssl-dev')
    c.sudo('apt-get install -yq make g++ pkg-config gcc build-essential')
    c.sudo('apt-get install -yq libfuse-dev libxml2 libxml2-dev curl libcurl3 libcurl3-dev')
    # Download
    c.sudo_cd('~', f'wget http://s3fs.googlecode.com/files/s3fs-{s3fs_version}.tar.gz'n)
    c.sudo_cd('~', f'tar xzvf s3fs-{s3fs_version}.tar.gz')
    c.sudo_cd(f'~/s3fs-{s3fs_version}', './configure --prefix=/usr')
    c.sudo_cd(f'~/s3fs-{s3fs_version}', 'make')
    c.sudo_cd(f'~/s3fs-{s3fs_version}', 'make install')
