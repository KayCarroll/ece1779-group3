import os

CONFIG_FILE = 'config.json'
CLOUDWATCH_NAMESPACE = 'MemCache Metrics 2'
CACHE_ID = os.environ.get('CACHE_ID', 0)
CACHE_BASE_URL = os.environ.get('CACHE_BASE_URL', 'http://127.0.0.1:5001')
# CACHE_HOST = os.environ.get('CACHE_HOST', '127.0.0.1:5002')
# CACHE_PORT = os.environ.get('CACHE_PORT', 5001)
AWS_ACCESS_KEY_ID = 'AKIARYPZNG6KRLLMQZ3X'
AWS_SECRET_ACCESS_KEY = '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'
#AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
#AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY'0
REGION_NAME = os.environ.get('REGION_NAME', 'us-east-1')
