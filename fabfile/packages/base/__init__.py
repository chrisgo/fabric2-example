import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
Base Packages
"""

def install(c):
    util.start()
    # Run an update
    c.sudo('apt-get update')
    #sudo('DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')
    c.sudo('apt-get install -yq default-mysql-client')
    c.sudo('apt-get install -yq curl ntp rsync')
    c.sudo('apt-get install -yq git-core vim htop ncdu')
    c.sudo('apt-get install -yq sshpass')
    #print("Install netdata")
    #netdata.install()
    #netdata.configure()
    # 8/31/18 CG: Get control over the journal
    # Gets too big https://askubuntu.com/questions/1012912/systemd-logs-journalctl-are-too-large-and-slow
    # Security stuff
    # Remove exim
    c.sudo('apt-get remove -yq exim4')
    c.sudo('apt-get install -yq fail2ban')
    c.sudo('apt-get install -yq unattended-upgrades')
    util.done()


def configure(c):
    util.start()
    # Set the timezone
    print('Setting Timezone')
    # Set timezone
    c.append(f'{c.config.project.timezone}', '/etc/timezone')
    c.sudo('dpkg-reconfigure -f noninteractive tzdata')
    # Make bash the default shell
    print('Settings /bin/bash as default shell')
    c.sudo(f'chsh -s /bin/bash {c.config.project.username}')
    # Make vim the default editor
    # https://unix.stackexchange.com/questions/73484/how-can-i-set-vi-as-my-default-editor-in-unix
    # add the following lines to bash_rc
    #run('echo \'export VISUAL=vim\' >> ~/.bashrc')
    #run('echo \'export EDITOR="$VISUAL"\' >> ~/.bashrc')
    #run('source ~/.bashrc')
    # http://shallowsky.com/blog/linux/ubuntu-default-browser.html
    # Set vim colorscheme
    # https://mediatemple.net/community/products/dv/204644480/enabling-vi-syntax-colors
    if (c.config.provider == 'vagrant'):
        return
    c.put_template('vimrc', f'/home/{c.config.project.name}/.vimrc')
    #sudo rm /etc/alternatives/gnome-www-browser
    # sudo ln -s /usr/local/firefox11/firefox /etc/alternatives/gnome-www-browser
    # sudo rm /etc/alternatives/x-www-browser
    # sudo ln -s /usr/local/firefox11/firefox /etc/alternatives/x-www-browser
    #sudo('update-alternatives --config editor')
    # Create folder for ssl certs
    if not c.exists(f'/home/{c.config.project.name}/ssl'):
        c.run(f'mkdir /home/{c.config.project.name}/ssl')
    util.done()


def add_keys(c):
    """
    Add keys that we can use for later
    """
    util.start()
    # (1) Don't do anything if vagrant
    if (c.config.provider == 'vagrant'):
        return
    # (2) Make .ssh directory if it does not exist
    if not c.exists(f'/home/{c.config.project.username}/.ssh'):
        c.run('mkdir ~/.ssh')
    # (3) Create the private/public key for the user on this server
    if not c.exists(f'/home/{c.config.project.username}/.ssh/id_rsa.pub'):
        print('... creating new SSH key')
        # Try to get rid of the prompts
        #prompts = []
        #prompts += expect('What is your name?','Jasper')
        #with expecting(prompts):
        #   expect_run('ssh-keygen -t rsa', pty=False)
        # http://unix.stackexchange.com/questions/69314/automated-ssh-keygen-without-passphrase-how
        # ssh-kegen -b 2048 -t rsa -f /tmp/sshkey -q -N ""
        #
        #run('ssh-keygen -t rsa', pty=False)
        c.run('ssh-keygen -t rsa -f /tmp/sshkey -q -N ""', pty=False)
        c.sudo('rm /tmp/sshkey')
    else:
        print('... creating new SSH key')
    # (4) Add any public keys to the domain user ~.ssh/authorized_keys
    util.done()
