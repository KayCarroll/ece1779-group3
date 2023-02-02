import datetime
from app import db


class CacheConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    capacity = db.Column(db.Float)
    replacement_policy = db.Column(db.String)


class CacheStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    cache_count = db.Column(db.Integer)
    cache_size = db.Column(db.Float)
    miss_rate = db.Column(db.Float)
    hit_rate = db.Column(db.Float)
    requests_served = db.Column(db.Integer)
