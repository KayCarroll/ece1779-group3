import datetime
from app import db

# TODO: Revisit the column types and correct them as needed

class CacheConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    capacity = db.Column(db.Integer)
    replacement_policy = db.Column(db.String)


class CacheStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # config_id = db.Column(db.Integer, db.ForeignKey('CacheConfig.id')) # Might not really need this, consider removing/changing
    cache_count = db.Column(db.Integer)
    cache_size = db.Column(db.Float)
    miss_rate = db.Column(db.Integer)
    hit_rate = db.Column(db.Integer)
    requests_served = db.Column(db.Integer)
