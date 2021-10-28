import datetime
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task
from patchwork import files
from fabfile.core import *

"""
NewRelic One
https://one.newrelic.com/launcher/apm-setup-page-nerdlets.setup-page-launcher?pane=eyJuZXJkbGV0SWQiOiJhcG0tc2V0dXAtcGFnZS1uZXJkbGV0cy5zZXR1cC1wYWdlIiwiYWdlbnQiOiJwaHAifQ&platform[accountId]=344636
"""

def install(c):
    """
    Install NewRelic One
    """
    util.start()
    # (1) Get the license key from the config
    #     a127721f502417b2c85385477b88474fd2a5ace4
    license_key = c.config.newrelic.key
    # (2) Get the signatures for the repos
    c.run('wget -O - https://download.newrelic.com/548C16BF.gpg | sudo apt-key add -')
    c.run('wget -O - https://download.newrelic.com/infrastructure_agent/gpg/newrelic-infra.gpg | sudo apt-key add -')
    # (3) Add the repos to the apt sources list
    if not c.exists('/etc/apt/sources.list.d/newrelic.list'):
        c.put_template('newrelic.list', '/etc/apt/sources.list.d/newrelic.list', sudo=True)
    # (4) Export some variables
    c.run('export NR_INSTALL_SILENT=1')
    c.run(f'export NR_INSTALL_KEY={license_key}')
    sudo_args = f'NR_INSTALL_SILENT=1 NR_INSTALL_KEY={license_key}'
    #c.sudo("sudo -E bash -c 'echo $NR_INSTALL_SILENT'")
    #c.sudo("sudo -E bash -c 'echo $NR_INSTALL_KEY'")
    print(sudo_args)
    # (5) Create the config file for the infrastructure agent
    #     license_key: a127721f502417b2c85385477b88474fd2a5ace4
    if not c.exists('/etc/newrelic-infra.yml'):
        c.sudo(f'bash -c "echo license_key: {license_key} > /etc/newrelic-infra.yml"')
    #
    #
    # (6) Run the apt-get update to get the latest repos from newrelic
    c.sudo('apt-get update')
    # (7) Install the infrastructure agent
    #https://one.newrelic.com/launcher/nr1-core.settings?pane=eyJuZXJkbGV0SWQiOiJzZXR1cC1uZXJkbGV0LnNldHVwLW9zIiwiZGF0YVNvdXJjZSI6IkRFQklBTiJ9
    #c.run('curl -s https://download.newrelic.com/infrastructure_agent/gpg/newrelic-infra.gpg | sudo apt-key add - && ')
    c.sudo('apt-get install -yq newrelic-infra')
    #
    #
    # TODO: Need to get silent mode working
    # https://docs.newrelic.com/docs/agents/php-agent/advanced-installation/silent-mode-install-script-advanced
    # https://discuss.newrelic.com/t/newrelic-install-not-respecting-environment-variables/24110
    # The license key needs to be there before installation per the documentation
    #c.sudo('bash -c "echo newrelic.license=%s > /etc/php/7.3/mods-available/newrelic.ini"' % license_key)
    #if not exists('/etc/php/7.3/fpm/conf.d/99-newrelic.ini'):
    #    c.sudo('ln -s /etc/php/7.3/mods-available/newrelic.ini /etc/php/7.3/fpm/conf.d/99-newrelic.ini')
    #if not exists('/etc/php/7.3/cli/conf.d/99-newrelic.ini'):
    #    c.sudo('ln -s /etc/php/7.3/mods-available/newrelic.ini /etc/php/7.3/cli/conf.d/99-newrelic.ini')
    #install = 'NR_INSTALL_SILENT=1 NR_INSTALL_KEY=%s apt-get install -yq newrelic-php5' % license_key
    #print install
    #c.sudo(install)
    #c.run('sudo NR_INSTALL_SILENT=1 NR_INSTALL_KEY=%s apt-get install -yq newrelic-php5' % license_key)
    # 12/16/20 CG: So far, nothing is really automating this yet and the only thing working is running this
    # manually once you are ssh'd into the server
    # sudo NR_INSTALL_SILENT=1 NR_INSTALL_KEY=a127721f502417b2c85385477b88474fd2a5ace4 apt-get install -yq newrelic-php5
    # sudo /etc/init.d/php7.3-fpm restart
    # sudo /etc/init.d/nginx restart
    # ls -la /var/log/newrelic
    #
    #
    # (8) Run the apt-get install for the PHP agent
    #     12/16/20 CG: Does not really work yet
    c.run(f'sudo {sudo_args} apt-get install -yq newrelic-php5')
    util.done()


def configure(c):
    """
    Configure license
    """
    util.start()
    #c.sudo('bash -c "echo newrelic.license=%s > /etc/php/7.3/mods-available/newrelic.ini"' % license_key)
    #c.sudo('ln -s /etc/php/7.3/mods-available/newrelic.ini /etc/php/7.3/fpm/conf.d/99-newrelic.ini')
    #c.sudo('ln -s /etc/php/7.3/mods-available/newrelic.ini /etc/php/7.3/cli/conf.d/99-newrelic.ini')
    c.sudo('/etc/init.d/php7.3-fpm restart')
    c.sudo('/etc/init.d/nginx restart')
    util.done()
