import paramiko
import os
import json
import datetime
import inspect
import time
import pprint
from invoke import Exit
from patchwork import files
from colorama import Fore, Back, Style
from fabric import Connection
from invoke import Collection
from fabric import Config
from fabric import task

# ==============================================================================
# Connection class that extends fabric.connection.Connection
# https://docs.fabfile.org/en/2.6/api/connection.html
# ==============================================================================

class Connection(Connection):
    """
    Class that extends fabric.connection.Connection so that we can add some
    additional methods and not have to do util._____()
    https://docs.fabfile.org/en/2.6/api/connection.html
    """

    def sudo_passthrough(self, command):
        """
        Emulates with sudo {command} as sometimes the built-in sudo does not work
        and gets weird stuff like permission denied
        """
        print(f'sudo_passthrough: {command}')
        self.run(f'sudo {command}')

    # ==========================================================================
    # Convenience functions for old fabric with cd(...):
    # ==========================================================================

    def run_with_cd(self, dir, command):
        """
        Emulates with cd(): from old fabric
        https://github.com/fabric/fabric/issues/1862
        """
        self.run(f'cd {dir} && {command}')

    def sudo_with_cd(self, dir, command):
        """
        Emulates with cd(): from old fabric
        https://github.com/fabric/fabric/issues/1862
        https://github.com/pyinvoke/invoke/issues/459
        """
        self.sudo(f'bash -c "cd {dir} && {command}"')

    # ==========================================================================
    # Convenience functions for old fabric file functions
    # These are now moved into patchwork so just wrapping them here
    # https://fabric-patchwork.readthedocs.io/en/latest/api/files.html
    # ==========================================================================

    def exists(self, path, sudo=False):
        """
        See if a path (file or directory) exists on the server
        https://fabric-patchwork.readthedocs.io/en/latest/api/files.html
        """
        return files.exists(self, path, sudo=sudo)

    def append(self, filename, text, escape=True, sudo=False):
        """
        Wraps the patchwork files.append
        https://fabric-patchwork.readthedocs.io/en/latest/api/files.html
        Arguments:
        c, filename, text, partial=False, escape=True, sudo=False, runner_method='run', runner=None
        3/19/21 CG: Patchwork files.append does not work for sudo so we are trying the
        workaround described here https://github.com/fabric/patchwork/issues/30
        """
        if (sudo):
            self.run(f'echo "{text}" | sudo tee -a {filename} > /dev/null')
        else:
            self.run(f'echo "{text}" >> {filename}')

    # ==========================================================================
    # Convenience function to EXIT right away and print FATAL on screen
    # ==========================================================================

    def exit(self, error):
        """
        Exit the entire fabric run, show FATAL in red and error message
        """
        host = Style.DIM + 'No host' + Style.RESET_ALL
        if self and self.has_key('host'):
            host = Fore.RED + self.host + Style.RESET_ALL
        elif isinstance(c, basestring):
            host = Fore.RED + c + Style.RESET_ALL
        print(Back.RED + ' FATAL ' + Style.RESET_ALL + ' ' + host)
        raise Exit('        ' + error)

    # ==========================================================================
    # Convenience function for old sed command that is no longer available
    # ==========================================================================

    def sed(self, filename, search, replace, sudo = False, mustache = False):
        """
        Remote sed
        https://stackoverflow.com/questions/55044243/how-to-make-changes-edit-on-a-file-present-on-remote-server-using-python-fabric
        3/12/21 CG: Wanted to use f-strings here but we can't get it to work, I am suspecting
        that this is because we are using a backport of the f-strings for python 2.7 so the
        backport package of `future-fstrings` may have a bug in it as we do the crazy curly
        brackets for our mustache-like tokens.  Once we fully move to python 3.6, we should
        investigate putting the commented out f-string version back in play
        """
        # (1) Make sure file exists
        if not files.exists(self, filename):
            print(f'Filename: {filename} does not exist')
            return
        # (2) Build the sed command
        if mustache:
            # (2.1) If mustache, add the curly brackets
            command = 'sed -i "s/{{{{{0}}}}}/{1}/g" '.format(search, replace) +filename
        else:
            # (2.2) Raw replace
            command = f'sed -i "s/{search}/{replace}/g" ' +filename
        # (3) Run in sudo mode or normal
        if sudo:
            print(command)
            self.sudo(command)
        else:
            self.run(command)

    # ==========================================================================
    # Convenience functions for some functions we had in util.py
    # This is some our own custom code but since we have to keep passing the
    # connection object into ALL the function calls, we are just wrapping
    # them here and using "self" to make it look better when we use these
    # functions
    # ==========================================================================

    def build_server_names(self):
        """
        Merge multiple entries for server names (usually an array)
        into a string suitable for nginx.  The first element will
        be the most specific, the last one is the generic

        For nginx:

            server_names wants to be specific to generic "bare"

        For letsencrypt:

            cli would prefer generic to specific "bare" first
            https://www.digitalocean.com/community/tutorials/how-to-set-up-let-s-encrypt-certificates-for-multiple-apache-virtual-hosts-on-ubuntu-14-04
            -d test.com -d www.test.com
        """
        # (1) If we don't find server_names, just return current host
        if 'server_names' not in self.config:
            return c.host
        # (2) If current role is not in server_names, also return current host
        if self.config.role not in self.config.server_names:
            return c.host
        # (3) Return the server names
        server_names = self.config.server_names[self.config.role]
        if server_names is None:
            server_names = self.host
        else:
            if not (isinstance(server_names, list)):
                server_names = [server_names]
                server_names.insert(0, self.host)
            else:
                server_names.insert(0, self.host)
        print(server_names)
        return server_names

    def sudo_put(self, source, target):
        """
        Convenience function to do a sudo put as the fabric2 library
        does not have an easy way to do this
        """
        # (2.1) Manipulate target
        _target = f'/tmp/{os.path.basename(target)}'
        # (2.2) Put in local directory (or /tmp)
        self.put(source, _target)
        # (2.3) Then do a sudo mv
        self.sudo(f'mv {_target} {target}')
        self.sudo(f'chown root:root {target}')


    def put_template(self, source, target, sudo=False):
        """
        Puts a file in the local package folder to a target location on server
        TODO: If sudo=True, we need to possibly copy the file to the user
        home directory first, then sudo move it to the final location
        """
        # (1) Build full path to source which is the directory this command
        #     was called from
        module_name = ''
        stack = inspect.stack()
        parentframe = stack[1][0]
        module = inspect.getmodule(parentframe)
        if module:
            module_pieces = (module.__name__).split('.')
            module_name = module_pieces[-1]
            _source = f'fabfile/packages/{module_name}/{source}'
        else:
            _source = f'fabfile/packages/{source}'
        # (2) If sudo, make the target a writable file first that is either
        #     in ~/{target} (user home dir) or /tmp/{target}
        if sudo:
            # (2.1) Manipulate target
            _target = f'/tmp/{os.path.basename(target)}'
            # (2.2) Put in local directory (or /tmp)
            self.put(_source, _target)
            # (2.3) Then do a sudo mv
            self.sudo(f'mv {_target} {target}')
            self.sudo(f'chown root:root {target}')
        else:
            # (2.4) sudo is false, so just do it normal
            print(_source)
            _target = target
            print(_target)
            self.put(_source, _target)

    def enabled(self, module):
        """
        Set if a module/feature is enabled or not
        """
        return self.config.get('enables').get(module, False)

    def environment(self):
        """
        Gets the environment
        """
        environment = self.config.get('environment')
        return environment

    def is_production(self):
        """
        See if server is in production
        """
        environment = self.config.get('environment')
        if (environment == 'PRODUCTION'):
            return True
        else:
            return False
