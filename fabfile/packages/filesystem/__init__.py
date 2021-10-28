import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Filesystem

11/17/20 CG: Also think about using the acl package to better control the directory
structure.  The "{_project_name}" (worker) and "www-data" (web server/nginx) are still
sometimes not cooperating and the sticky tag on the directory and chmod are not working
so if they are sharing a folder, the writes fight each other

```
# Install package
sudo apt-get install acl
# Check to see current permissions and if ACL is on
getfacl /tmp/s3fs
getfacl /tmp/{_project_name}
# Set the acl for the directories
setfacl -m u:{_project_name}:rwx,u:www-data:rwx /tmp/s3fs
setfacl -m u:{_project_name}:rwx,u:www-data:rwx /tmp/{_project_name}
# Set the DEFAULT acl for the directories
setfacl -m default:u:{_project_name}:rwx,default:u:www-data:rwx /tmp/s3fs
setfacl -m default:u:{_project_name}:rwx,default:u:www-data:rwx /tmp/{_project_name}
```

https://www.thegeekdiary.com/unix-linux-access-control-lists-acls-basics/

"""

def install(c):
    util.start()
    c.sudo('apt-get install -y acl')
    util.done()

def configure(c):
    """
    Configure
    """
    util.start()
    # Create document root
    mount_root = env.config.get('mount_root')
    aws_buckets = env.aws_buckets if ('aws_buckets' in env) else ""
    #if ('%s' in document_root):
    #    mount_root = mount_root % env.git_project.lower()
    # Create document root directory if it doesn't exist
    #if not exists(mount_root):
    #    c.sudo("mkdir -m 775 -p %s" % mount_root)
    # Also load up the cleanup script into the cron area
    if (c.enabled('s3fs') and aws_buckets):
        print('adding s3fs cache system cleanup.sh')
        for aws_bucket in aws_buckets:
            mount = aws_bucket['mount']
            bucket_name = aws_bucket['name']
            add_cleanup(mount, bucket_name)
    else:
        print('no s3fs cache system to clean up')
    util.done()

def mkdirs(directories):
    """
    Create the directories needed for the project
    """
    util.start()
    if (directories):
        for directory in directories:
            print("Processing dir: %s" % directory)
            if not c.exists(directory):
                c.sudo(f'mkdir -m 777 -p {directory}')
    util.done()

def add_cleanup(mount, bucket_name, days = 14):
    """
    Add a cleanup dir for a specific folder
    """
    util.start()
    # (1) Build the cleanup file
    #     Note: shell script cannot have an extension (cleanup.sh will not work)
    #     https://www.petefreitag.com/item/847.cfm
    cleanup_sh = f'/etc/cron.daily/cleanup-{mount}'
    # (2) If file exists, delete it
    if c.exists(cleanup_sh):
        print(f'Found old cron job for cleanup of {mount}, deleting ...')
        c.sudo(f'rm -fR {cleanup_sh}')
    # (3) Create new cron job
    print(f'adding cron job for cleanup of bucket: {bucket_name} (mount: {mount})')
    c.put_template('etc_cron_cleanup-s3fs.sh', cleanup_sh, sudo=True)
    c.sed(cleanup_sh, '{{bucket_name}}', '%s' % bucket_name, sudo=True)
    c.sed(cleanup_sh, '{{mount}}', '%s' % mount, sudo=True)
    c.sed(cleanup_sh, '{{days}}', '%s' % days, sudo=True)
    c.sudo(f'chown root:root {cleanup_sh}')
    c.sudo(f'chmod +x {cleanup_sh}')
    util.done()
