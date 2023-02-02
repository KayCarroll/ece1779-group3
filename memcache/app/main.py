import logging

from flask import json, request
from app import webapp, db, cache
from app.models import CacheConfig, CacheStats

LOG_FORMAT = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
logging.getLogger('apscheduler').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def set_initial_cache_config():
    with webapp.app_context():
        config = CacheConfig.query.order_by(CacheConfig.created_time.desc()).first_or_404()
        cache.update_config(config.replacement_policy, config.capacity)
    return config


def store_memcache_statistics():
    with webapp.app_context():
        # TODO: Do some checks/tests to make sure that using the db object in this function while
        # its is being run in a separate thread by the scheduler won't be an issue.
        stats = CacheStats(**cache.get_statistics())
        db.session.add(stats)
        db.session.commit()


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
