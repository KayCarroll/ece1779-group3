import atexit
import json

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.memcache import MemCache

CONFIG_FILE = 'config.json'

webapp = Flask(__name__)
webapp.config.from_file(CONFIG_FILE, load=json.load)

db = SQLAlchemy()
db.init_app(webapp)

cache = MemCache()

from app.main import set_initial_cache_config, store_memcache_statistics

set_initial_cache_config()

scheduler = BackgroundScheduler()
scheduler.add_job(store_memcache_statistics, trigger='interval', seconds=5)
scheduler.start()
atexit.register(lambda: scheduler.shutdown(wait=False))
