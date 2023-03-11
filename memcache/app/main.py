import boto3
import datetime
import logging

from flask import json, request
from app import webapp, db, cache
from app.constants import CACHE_BASE_URL, CLOUDWATCH_NAMESPACE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME
from app.models import CacheConfig, CacheStatus

LOG_FORMAT = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
for module_name in ['apscheduler', 'botocore', 'urllib3']:
    logging.getLogger(module_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
boto_client = boto3.client('cloudwatch', aws_access_key_id=AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME)


def set_initial_cache_config():
    with webapp.app_context():
        config = CacheConfig.query.order_by(CacheConfig.created_time.desc()).first_or_404()
        cache.update_config(config.replacement_policy, config.capacity)
    return config


def set_cache_status():
    with webapp.app_context():
        cache_entry = CacheStatus.query.get(cache.id)
        if cache_entry:
            cache_entry.is_active = cache.is_active
            cache_entry.last_updated = datetime.datetime.utcnow()
        else:
            cache_entry = CacheStatus(id=cache.id, is_active=cache.is_active, base_url=CACHE_BASE_URL)
            db.session.add(cache_entry)

        db.session.commit()


def store_memcache_statistics():
    if cache.is_active:
        cache_stats = cache.get_statistics()
        metric_data = [{'MetricName': key, 'Dimensions': [{'Name': 'ID', 'Value': str(cache.id)}], 'Value': val} for key, val in cache_stats.items()]
        boto_client.put_metric_data(Namespace=CLOUDWATCH_NAMESPACE, MetricData=metric_data)
        logger.debug(f'Updated MemCache metrics: {cache_stats}')


@webapp.route('/get_image/<key>', methods=['GET'])
def get_image(key):
    """Get an image from the cache with the given key.
    """
    value = cache.get_value(key)

    if value:
        response = webapp.response_class(response=json.dumps(value), status=200,
                                         mimetype='application/json')
    else:
        response = webapp.response_class(response=json.dumps('Unknown key'), status=400,
                                         mimetype='application/json')
    return response


@webapp.route('/get_lru_keys', methods=['GET'])
def get_keys():
    """Get a list of all keys currently in the cache ordered from least to most recently used.

    Note: This route is mainly for testing/debugging purposes.
    """
    ordered_keys = cache.get_keys_ordered_by_lru()
    response = webapp.response_class(response=json.dumps(ordered_keys), status=200,
                                     mimetype='application/json')

    return response


@webapp.route('/cache_image', methods=['POST'])
def cache_image():
    """Put a new key-value pair item into the cache.

    Note: Current assumption is that the received value is a base64 encoded string.
    """
    key = request.form.get('key')
    value = request.form.get('value')

    try:
        cache.put_item(key, value)
        response = webapp.response_class(response=json.dumps('OK'), status=200,
                                        mimetype='application/json')
    except ValueError:
        response = webapp.response_class(response=json.dumps('Invalid value'), status=400,
                                         mimetype='application/json')
    return response


@webapp.route('/clear_cache', methods=['POST'])
def clear_cache():
    """Clear the cache.
    """
    cache.clear()
    response = webapp.response_class(response=json.dumps('OK'), status=200,
                                     mimetype='application/json')
    return response


@webapp.route('/invalidate_key', methods=['POST'])
def invalidate_key():
    """Invalidate a key in the cache by removing the key-value pair from the cache.
    """
    key = request.form.get('key')

    try:
        cache.invalidate_key(key)
        response = webapp.response_class(response=json.dumps('OK'), status=200,
                                         mimetype='application/json')
    except KeyError as e:
        logger.error(f'Unable to invalidate key {key} due to exception - {e}')
        response = webapp.response_class(response=json.dumps('Unknown key'), status=400,
                                         mimetype='application/json')
    return response


@webapp.route('/refresh_configuration', methods=['POST'])
def refresh_configuration():
    """Update the cache configuration by fetching the latest configuration from the cache_config table.
    """
    config = CacheConfig.query.order_by(CacheConfig.created_time.desc()).first()

    if config:
        cache.update_config(config.replacement_policy, config.capacity)
        response = webapp.response_class(response=json.dumps('OK'), status=200,
                                         mimetype='application/json')
    else:
        response = webapp.response_class(response=json.dumps('Config not found'), status=400,
                                         mimetype='application/json')
    return response


@webapp.route('/activate', methods=['POST'])
def activate_cache():
    """Activate the cache if not already active.
    """
    # TODO: Add logging and check if any additional logic needed to activate.
    if not cache.is_active:
        cache.activate()
        set_cache_status()

    response = webapp.response_class(response=json.dumps('OK'), status=200,
                                     mimetype='application/json')
    return response


@webapp.route('/deactivate', methods=['POST'])
def deactivate_cache():
    """Deactivate the cache if currently active.
    """
    # TODO: Add logging and check if any additional logic needed to deactivate.
    if cache.is_active:
        cache.deactivate()
        set_cache_status()

    response = webapp.response_class(response=json.dumps('OK'), status=200,
                                     mimetype='application/json')
    return response
