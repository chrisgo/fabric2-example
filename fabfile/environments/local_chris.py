# Developer: Chris

config = {
    'provider':             'vagrant',
    'connect_kwargs': {
        'password':         'vagrant',
    },
    'mount_root':           '/vagrant',
    'branch':               'master',               # branch
    'environment':          'DEVELOPMENT',
    'server_names': {
        'www':              ['chris-dev-www1.domain.com'],
    },
    'hostnames': {
        #'cron':             ['chris-dev-www.domain.com'],
        'database':         ['chris-dev-www1.domain.com'],
        'database_master':  ['chris-dev-www1.domain.com'],
        'database_slave':   [
                              'chris-dev-www1.domain.com',
                             ],
        #'node':             ['chris-dev-nod1.domain.com'],
        #'resque':           ['chris-dev-www.domain.com'],
        #'search':           ['chris-dev-www.domain.com'],
        #'worker':           ['chris-dev-www1.domain.com'],
        #'www':              ['chris-dev-www1.domain.com'],
        'www':              ['chris-dev-www1.domain.com'],
    },
    'enables': {
        'ssl':              True,
        's3fs':             False,
        'automysqlbackup':  False,
        'papertrail':       False,
        'certbot':          False,
    },
}
