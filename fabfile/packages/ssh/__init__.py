import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
SSH

9/26/20 CG: Running the PCI Server Scan (sysnet via https://pci.worldpay.com) finds that the
Debian 10 (stable) "buster" openssh of 1:7.9p1-10+deb10u2 has a CVE vulnerability that has a
status of vulnerable and it looks like it will take a while to patch
https://security-tracker.debian.org/tracker/CVE-2019-16905

For now, to pass the PCI Server Scan (this is the only test that is failing with PCI Compliant = NO)
we are going to have to update this to OpenSSH 8.1 or higher and here is the process we found
Tested on dev-www1.{_project_name}.com and it seems to work well

https://www.tecmint.com/install-openssh-server-from-source-in-linux/

```
ssh -V
sudo apt-get update
sudo apt install build-essential zlib1g-dev libssl-dev
sudo mkdir /var/lib/sshd
sudo chmod -R 700 /var/lib/sshd/
sudo chown -R root:sys /var/lib/sshd/
sudo useradd -r -U -d /var/lib/sshd/ -c "sshd privsep" -s /bin/false sshd
wget https://mirrors.sonic.net/pub/OpenBSD/OpenSSH/portable/openssh-8.3p1.tar.gz
tar -xzf openssh-8.3p1.tar.gz openssh-8.3p1
cd openssh-8.3p1/
./configure -h
sudo apt install libpam0g-dev libselinux1-dev
./configure --with-md5-passwords --with-pam --with-selinux --with-privsep-path=/var/lib/sshd/ --sysconfdir=/etc/ssh
make
sudo make install
sudo /etc/init.d/ssh restart
```

At some point, we probably will default back to the default debian packages as the build takes
forever ~10 minutes on each server

9/27/20 CG: So the above does not work because openssh-server is still reporting as 1.79
using sudo /etc/init.d/ssh restart and the solution is creating our own backport from bullseye
- https://serverfault.com/questions/1035472/upgrade-to-openssh-8-3-server-on-debian-10-buster
- https://wiki.debian.org/SimpleBackportCreation
- https://packages.debian.org/search?suite=bullseye&searchon=names&keywords=openssh-server
So what we are going to do is test this on a new server dev-www2.{_project_name}.com and see
if we can actually make this work and have the PCI scan report the correct version of openssh 1.83

```
sudo apt-get install packaging-dev debian-keyring devscripts equivs
??? rmadison openssh-server --architecture amd64 OR
??? rmadison openssh-server --architecture i386
sudo vi /etc/apt/sources.list.d/testing.list
  # Debian testing packages sources
  deb-src http://deb.debian.org/debian/ testing main
apt update
apt source openssh-server/testing
cd openssh-8.3p1
sudo mk-build-deps --install --remove
dch --bpo (use vi, save file using Esc :w! then Esc ZZ)
fakeroot debian/rules binary
sudo apt-get install apt-file
apt-file update
apt-file search Debian/Debhelper/Sequence/runit.pm
sudo apt-get install dh-runit
```

9/28/20 CG: The above does not work


"""

def install(c):
    util.start()
    #c.sudo('apt-get install -y ufw')
    util.done()


def configure(c):
    util.start()
    util.done()


def backport_bullseye(c):
    """
    Doing a custom backport of openssh from bullseye
    https://packages.debian.org/search?suite=bullseye&searchon=names&keywords=openssh-server
    Shows the correct version 1:8.3p1-1 (PCI Scan wants anything >= 8.1)
    """
    util.start()
    util.done()


def install_83(c):
    """
    Install OpenSSH 8.3
    9/27/20 CG: The install worked and ssh -V reports 8.3 but the openssh-server is still
    reporting as 1.79 which is still failing the PCI Scan
    """
    util.start()
    version = 'openssh-8.3p1'
    c.run('ssh -V')
    c.sudo('apt-get update')
    c.sudo('apt install -yq build-essential zlib1g-dev libssl-dev')
    c.sudo('apt install -yq libpam0g-dev libselinux1-dev')
    c.sudo('mkdir /var/lib/sshd')
    c.sudo('chmod -R 700 /var/lib/sshd/')
    c.sudo('chown -R root:sys /var/lib/sshd/')
    c.sudo('useradd -r -U -d /var/lib/sshd/ -c "sshd privsep" -s /bin/false sshd')
    c.run(f'wget https://mirrors.sonic.net/pub/OpenBSD/OpenSSH/portable/{version}/.tar.gz')
    c.run(f'tar -xzf {version} .tar.gz {version}')
    #c.run('./configure -h')
    c.run_with_cd(f'{version}/', './configure --with-md5-passwords --with-pam --with-selinux --with-privsep-path=/var/lib/sshd/ --sysconfdir=/etc/ssh')
    c.run_with_cd(f'{version}/', 'make')
    c.sudo_with_cd(f'{version}/', 'make install')
    c.sudo('/etc/init.d/ssh restart')
    c.run('ssh -V')
    util.done()
