import datetime
from app import db


class CacheStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean)
    base_url = db.Column(db.String)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
