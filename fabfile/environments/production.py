# Servers

config = {
    'provider':             'digitalocean',
    'mount_root':           '/mnt/s3fs',
    'branch':               'master',               # branch
    'environment':          'PRODUCTION',
    'server_names': {
        'bitwarden':        ['pass.domain.com'],
        'node':             ['prd-nod.domain.com'],
        'redis':            ['redis.domain.com'],
        'rocketchat':       ['chat.domain.com'],
        'socket':           ['socket.domain.com'],
        'www':              ['www.domain.com', 'domain.com'],
    },
    'hostnames': {
        'bitwarden':        ['prd-bit1.domain.com'],
        'cron':             ['prd-wrk1.domain.com'],
        'database':         [
                             'prd-mdb1.domain.com',
                             'prd-mdb2.domain.com',
                             'prd-mdb3.domain.com',
                             'prd-mdb4.domain.com',
                             #'prd-mdb5.domain.com',
                             #'prd-mdb6.domain.com',
                             'prd-mdb7.domain.com',
                            ],
        'database_master':  ['prd-mdb1.domain.com'],   # if not here, SLAVE
        'node':             ['prd-nod1.domain.com'],
        'proxy':            ['prd-pxy1.domain.com',
                             'prd-pxy2.domain.com',
                            ],
        'puppet':           ['prd-ppt1.domain.com'],
        'redis':            [
                             'prd-rds1.domain.com',
                             'prd-rds2.domain.com',
                             #'prd-rds3.domain.com',
                             #'prd-rds4.domain.com'
                            ],
        'rocketchat':       ['prd-rkt1.domain.com'],
        #'search':           ['prd-sol1.domain.com'],
        'socket':           ['prd-sok1.domain.com'],
        'www':              [
                             'prd-www1.domain.com',
                             'prd-www2.domain.com',
                             'prd-www3.domain.com',
                             'prd-www4.domain.com',
                             'prd-www5.domain.com',
                             'prd-www6.domain.com',
                             'prd-www7.domain.com',
                             'prd-www8.domain.com',
                             #'prd-www9.domain.com',
                             #'prd-api1.domain.com',
                            ],
        'worker':           [
                             'prd-wrk1.domain.com',
                             'prd-wrk2.domain.com',
                             'prd-wrk3.domain.com',
                             'prd-wrk4.domain.com',
                             'prd-wrk5.domain.com',
                             'prd-wrk6.domain.com',
                             #'prd-wrk7.domain.com',
                             #'prd-wrk8.domain.com',
                             #'prd-wrk9.domain.com',
                            ],
    },
    'enables': {
        'ssl':              True,
        's3fs':             True,
        'automysqlbackup':  True,
        'papertrail':       True,
        'certbot':          False,
    },
}
