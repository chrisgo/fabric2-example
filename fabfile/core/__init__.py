import pprint
import importlib
from colorama import Fore, Back, Style, Cursor

#__all__ = [
#    'connection',
#    'core',
#    'util',
#]


def confirm(config, role):
    """
    ......... <production> confirm action/command for PROD environment
    """
    # (4) Get the 2nd argument passed into fabric to pick up the hosts we care about
    #role = sys.argv[2]
    #print(role)
    # (5) Load list of hosts for display
    if config.hostnames[role]:
        hosts = config.hostnames[role]
        print('\n')
        print(Back.CYAN + Style.BRIGHT + ' HOSTS ' + Style.RESET_ALL + ' PRODUCTION')
        if len(hosts) > 0:
            if len(hosts) > 1:
                print('        ' + '\n        '.join(hosts) + Style.RESET_ALL)
            else:
                print('        ' + ''.join(hosts) + Style.RESET_ALL)
    else:
        print(Back.RED + Style.BRIGHT + 'Warning: NO HOSTNAMES' + Style.RESET_ALL)
    print('\n\n')
    check = input('Updating PRODUCTION, please type project name: ')
    print (check)
    if (check.upper() != config.project.name.upper()):
        print('\n')
        print(Back.RED + Style.BRIGHT + ' ABORT ' + Style.RESET_ALL + ' fabric task aborted')
        print(Fore.RED + '        incorrect project name entered' + Style.RESET_ALL)
        print('\n\n')
        exit()
