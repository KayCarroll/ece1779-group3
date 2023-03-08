import atexit
import json

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.constants import CONFIG_FILE, CACHE_ID
from app.memcache import MemCache

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
