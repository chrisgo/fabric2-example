# Servers

config = {
    'provider':             'digitalocean',
    'mount_root':           '/tmp/s3fs',
    'branch':               'master',               # branch
    'environment':          'STAGING',
    'server_names': {
        'www':              ['staging.domain.com'],
        'node':             ['stg-nod.domain.com'],
    },
    'hostnames': {
        'cron':             ['stg-www1.domain.com'],
        'database':         ['dev-www1.domain.com'],
        'node':             ['stg-nod1.domain.com'],
        'redis':            ['dev-rds1.domain.com'],
        #'search':           ['dev-www1.domain.com'],
        'worker':           ['stg-www1.domain.com'],
        'www':              ['stg-www1.domain.com'],
    },
    'enables': {
        'ssl':              True,
        's3fs':             False,
        'automysqlbackup':  False,
        'papertrail':       True,
        'certbot':          False,
    },
}
