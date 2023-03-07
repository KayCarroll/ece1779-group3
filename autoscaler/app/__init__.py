import atexit
import json
# import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.autoscaler import AutoScaler, ScalingMode

CONFIG_FILE = 'config.json'
CLOUDWATCH_NAMESPACE = 'MemCache Metrics'

webapp = Flask(__name__)
webapp.config.from_file(CONFIG_FILE, load=json.load)

db = SQLAlchemy()
db.init_app(webapp)

scaler = AutoScaler(ScalingMode.MANUAL)

from app.main import auto_scale

scheduler = BackgroundScheduler()
scheduler.add_job(auto_scale, trigger='interval', seconds=60)
scheduler.start()
atexit.register(lambda: scheduler.shutdown(wait=False))
