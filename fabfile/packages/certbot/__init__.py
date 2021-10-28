import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Certbot (Letsencrypt)

Installs certbot so that we can get wildcard certificates
This uses a specific env variable to determine which server
is the one that does the renewal so that not all servers have
to have certbot installed.

The main certbot server (usually dev-www1.domain.com) will
install certbot and the ~/digitalocean.ini file.

During renewal, the main certbot server will perform the renewal
and pull down the files from the server and put it in the right spot
in the environments folder.  If server is NOT the main certbot server,
the renewal will copy the latest pem files up to the correct location
on the server

"Live" certificates are linked from where certbot creates
them to their main location which is

/etc/letsencrypt/live/domain.com/privkey.pem;
/etc/letsencrypt/live/domain.com/fullchain.pem;

"""

def install(c):
    util.start()
    # Only install certbot if this is the designated host
    if c.config.certbot.host == c.host:
        print('Installing Certbot client ...')
        c.sudo('apt-get install -yq certbot')
        c.sudo('apt-get install -yq python3-certbot-dns-digitalocean')
        c.sudo('apt-get install -yq python3-certbot-dns-route53')
        # Check to make sure letsencrypt folder exists
        if not c.exists('/etc/letsencrypt'):
            print('Creating /etc/letsencrypt directory ...')
            c.sudo('mkdir /etc/letsencrypt')
        # Delete old digitalocean.ini file
        if c.exists('/etc/letsencrypt/digitalocean.ini'):
            print('Deleting old /etc/letsencrypt/digitalocean.ini file ...')
            c.sudo('rm /etc/letsencrypt/digitalocean.ini')
        print("Creating digitalocean.ini file ...")
        # Delete old aws config file
        if c.exists('/root/.aws/config'):
            print('Deleting old /root/.aws/config file ...')
            c.sudo('rm /root/.aws/config')
        if c.config.certbot.dns == 'aws':
            print("Creating /root/.aws/config file ...")
            c.sudo('mkdir /root/.aws')
            c.put_template('aws_config', '/root/.aws/config', sudo=True)
            c.sed('/root/.aws/config', '{{access_key}}', c.config.aws.access_key, sudo=True)
            c.sed('/root/.aws/config', '{{secret_key}}',  c.config.aws.secret_key, sudo=True)
        else:
            print("Creating digitalocean.ini file ...")
            c.put_template('digitalocean.ini', '/etc/letsencrypt/digitalocean.ini', sudo=True)
            c.sed('/etc/letsencrypt/digitalocean.ini', '{{digitalocean_token}}', c.config.digitalocean.token, sudo=True)
            c.sudo('chmod 600 /etc/letsencrypt/digitalocean.ini')
    else:
        print('Not installing Certbot client ...')
    util.done()


def configure(c):
    util.start()
    # If this host is NOT the certbot_host, copy the certificates up
    if c.host != c.config.certbot.host:
        letsencrypt_dir = f'/etc/letsencrypt/live/{c.config.project.name}.com'
        print('NOT certbot host, we need to copy certificates up ...')
        if not c.exists(letsencrypt_dir):
            print('Creating /etc/letsencrypt directory ...')
            c.sudo(f'mkdir -p {letsencrypt_dir}')
        c.sudo_put('fabfile/environments/ssl/privkey.pem', letsencrypt_dir)
        c.sudo_put('fabfile/environments/ssl/fullchain.pem', letsencrypt_dir)
    else:
        print('Running certbot ...')
        print("Checking /etc/letsencrypt/live folder ...")
        if c.exists("/etc/letsencrypt/live"):
            print("Deleting 'live' folder ...")
            c.sudo("rm -fR /etc/letsencrypt/live")
        print("Running certbot command ...")
        _certbot_dns = c.config.certbot.dns
        if (_certbot_dns == 'aws'):
            _certbot_dns = 'route53'
        print(f' ... going to {c.config.certbot.dns} DNS Wildcard Certificate')
        cmd = 'certbot certonly ' \
              ' --agree-tos ' \
              ' --preferred-challenges dns ' \
              ' --noninteractive ' \
              f' --dns-{_certbot_dns} ' \
              f' --dns-digitalocean-credentials /etc/letsencrypt/digitalocean.ini ' \
              ' --server https://acme-v02.api.letsencrypt.org/directory ' \
              f' -m tech@{c.config.project.name}.com ' \
              f' -d {c.config.project.name}.com -d *.{c.config.project.name}.com'
        c.sudo(cmd)
    util.done()


def renew_certificate():
    """
    Renew SSL certificate
    """
    util.start()
    util.done()


def renew_cert(c):
    """
    Renew SSL Cert
    """
    print('==================================================')
    print('Renew Letsencrypt SSL Cert (Common)')
    print('==================================================')
    letsencrypt_dir = f'/etc/letsencrypt/live/{c.config.certbot.domain}'
    if c.host == c.config.certbot.host:
        print('Renewing SSL Cert ...')
        c.sudo('certbot renew')
        c.get(f'{letsencrypt_dir}/privkey.pem', 'fabfile/environments/ssl/privkey.pem')
        c.get(f'{letsencrypt_dir}/fullchain.pem', 'fabfile/environments/ssl/fullchain.pem')
        print(yellow('SSL cert files have been copied, do a commit'))
        #local('openssl x509 -dates -noout < fabfile/environments/ssl/fullchain.pem')
    else:
        print(f'Copying SSL Cert to {c.host}')
        #local('openssl x509 -dates -noout < fabfile/environments/ssl/fullchain.pem')
        if not c.exists(letsencrypt_dir):
            c.sudo(f'mkdir -p {letsencrypt_dir}' % l)
        c.sudo_put('fabfile/environments/ssl/privkey.pem', f'{letsencrypt_dir}/privkey.pem')
        c.sudo_put('fabfile/environments/ssl/fullchain.pem', f'{letsencrypt_dir}/fullchain.pem')
        c.sudo('/etc/init.d/nginx restart')
    # Done
    print('==================================================')
    print('... done Renew Letsencrypt SSL Cert (Common)')
    print('==================================================')
