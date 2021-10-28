# Base environment config

config = {
    'connect_kwargs': {
        'password': 'project_password',
    },
    'project': {
        'name': 'project_name',
        'username': 'project_name',
        'password': 'project_password',
        'timezone': 'UTC',
        'checkout': {
            'root_dir': '~/checkout',                           # checkout dir
            'source_dir': 'src/php',                            # source folder
        },
        'server': {
            'root_dir': '/var/www/project_name/php',            # Server root
            'public_dir': '/var/www/project_name/php/public',   # Nginx web root
        },
        'databases': [
            'project_name',
        ],
        'dirs': [
            's3fs/database',
            's3fs/database/automysqlbackup',
            's3fs/documents',
            's3fs/messages',
            's3fs/tests',
            's3fs/temp',
        ],
        'packages': [
            'imagemagick',
            'libdmtx-dev',
            'libdmtx0b',
            'pdftk',
            'poppler-utils',
        ],
    },
    'automysqlbackup': {
        'dir': '/var/backups/automysqlbackup',
        'host': 'prd-mdb9.domain.com',
    },
    'aws': {
        'region': 'us-west-1',
        'buckets': [{
            'name': 's3fs.domain.com',
            'mount': 's3fs',
            'access_key': '',
            'secret_key': '',
        }],
    },
    'certbot': {
        'host': 'dev-www1.domain.com',
        'dns': 'aws',
        'domain': 'domain.com',
    },
    'digitalocean': {
        'client_id': '',
        'token': '',
    },
    'fabric': {
        #'server_role': '',
        #'providers': ['vagrant', 'digitalocean', 'linode', 'aws'],
        #'server_roles': ['cron', 'database', 'node', 'proxy', 'puppet', 'redis', 'search', 'socket', 'worker','www'],
    },
    'git': {
        'host': 'gitlab.com',
        'project': 'project_name/web.git',
    },
    'newrelic': {
        'key': '', # NewRelic One
    },
    'papertrail': {
        'url': 'logs.papertrailapp.com',
        'port': '',
    },
    'php': {
        'version': '7.4',
        'api_version': '20190902',
        #'version': '8.0',
        #'api_version': '20200930',
    }
    #'redis': {
    #    'host': '',
    #    'port': '',
    #    'password': '',
    #    'db': '',
    #},
}
