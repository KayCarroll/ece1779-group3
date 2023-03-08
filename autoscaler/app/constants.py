import os

CONFIG_FILE = 'config.json'
CLOUDWATCH_NAMESPACE = 'MemCache Metrics'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.environ.get('REGION_NAME', 'us-east-1')
