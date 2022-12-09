import os

os.environ['ENABLED_EXTENSIONS'] = ','.join([
    'query',
    'sort',
    'fields',
    'pagination',
    'context',
])

from stac_fastapi.pgstac.app import handler  # noqa: F401, E402
