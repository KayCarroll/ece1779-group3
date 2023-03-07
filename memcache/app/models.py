import datetime
from app import db


class CacheConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    capacity = db.Column(db.Float)
    replacement_policy = db.Column(db.String)


class CacheStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean)
    cache_host = db.Column(db.String)
    # cache_port = db.Column(db.String)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
