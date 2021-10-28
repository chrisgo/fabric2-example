import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Generate a self-signed SSL cert

http://crohr.me/journal/2014/generate-self-signed-ssl-certificate-without-prompt-noninteractive-mode.html
http://aruljohn.com/info/self-signed-certificate/
https://support.mozilla.org/en-US/questions/995117

"""

def install(c):
    util.start()
    #prefix = "chris-dev-d8"
    #c.run_with_cd('~', "openssl req -subj f"/CN='{prefix}.{c.config.project.name}.com/O={c.config.project.name}/C=US' -new -newkey rsa:2048 -sha256 -days 365 -nodes -x509 -keyout server.key -out server.crt")
    util.done()

def configure(c):
    util.start()
    util.done()

"""
Generate a self-signed certificate
TODO: Handle more than one server name
"""
def self_signed(c):
    util.start()
    # Get some env variables
    #project_name = env.project_name
    #base_user = env.base_user
    #server_name = env.aws_buckets if ('aws_buckets' in env) else ""
    #server_names = env.config.get("server_names")[env.server_role]
    #server_name = server_names[0]
    # Generate a self-signed certificate
    #c.run_with_cd('~', 'openssl genrsa -des3 -passout pass:x -out server.pass.key 2048')
    #c.run_with_cd('~', 'openssl rsa -passin pass:x -in server.pass.key -out server.key')
    #c.run_with_cd('~', 'rm server.pass.key')
    #c.run_with_cd('~', 'openssl req -new -key server.key -out server.csr -subj "/C=US/ST=California/L=/O=%s/OU=/CN=%s"' % (project_name, server_name))
    #c.run_with_cd('~', 'openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt')
    # Copy files to fake locations for letsencrypt
    #folder = f'/etc/selfsignedssl/live/{server_name}'
    #if c.exists(folder):
    #    c.sudo(f'rm -fR {folder}')
    #c.sudo(f'mkdir -p {folder}')
    #c.sudo(f'cp /home/{base_user}/server.crt /etc/selfsignedssl/live/{server_name}/server.crt')
    #c.sudo(f'cp /home/{base_user}/server.key /etc/selfsignedssl/live/{server_name}/server.key')
    util.done()
