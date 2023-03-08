import atexit
import json
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.memcache import MemCache

CONFIG_FILE = 'config.json'
CLOUDWATCH_NAMESPACE = 'MemCache Metrics'
CACHE_ID = os.environ.get('CACHE_ID', 0)
CACHE_BASE_URL = os.environ.get('CACHE_BASE_URL', 'http://127.0.0.1:5001')
# CACHE_HOST = os.environ.get('CACHE_HOST', '127.0.0.1:5002')
# CACHE_PORT = os.environ.get('CACHE_PORT', 5001)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.environ.get('REGION_NAME', 'us-east-1')


webapp = Flask(__name__)
webapp.config.from_file(CONFIG_FILE, load=json.load)

db = SQLAlchemy()
db.init_app(webapp)

cache = MemCache(CACHE_ID)

from app.main import set_initial_cache_config, set_cache_status, store_memcache_statistics

set_initial_cache_config()
set_cache_status()

scheduler = BackgroundScheduler()
scheduler.add_job(store_memcache_statistics, trigger='interval', seconds=5)
scheduler.start()
atexit.register(lambda: scheduler.shutdown(wait=False))
