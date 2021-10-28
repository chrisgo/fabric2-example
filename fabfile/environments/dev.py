# Servers

config = {
    'provider':             'digitalocean',
    'mount_root':           '/tmp/s3fs',
    'branch':               'master',               # branch
    'environment':          'DEVELOPMENT',
    'server_names': {
        'www':              ['dev-www.domain.com'],
        'node':             ['dev-nod.domain.com'],
    },
    'hostnames': {
        'cron':             ['dev-www2.domain.com'],
        'database':         ['dev-www2.domain.com'],
        'node':             ['dev-nod2.domain.com'],
        'redis':            ['dev-rds2.domain.com'],
        #'search':           ['dev-www1.domain.com'],
        'worker':           ['dev-www2.domain.com'],
        'www':              ['dev-www2.domain.com'],
    },
    'enables': {
        'ssl':              True,
        's3fs':             False,
        'automysqlbackup':  False,
        'papertrail':       True,
        'certbot':          True,
    },
}
