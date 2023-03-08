import atexit
import json

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.constants import CONFIG_FILE
from app.autoscaler import AutoScaler, ScalingMode

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
