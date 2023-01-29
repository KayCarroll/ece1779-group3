import logging

from flask import json, render_template, request
from app import webapp, db, cache
# from app.models import CacheConfig, CacheStats

LOG_FORMAT = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# TODO: Add in logging and docstrings
# TODO: Actually test connecting to and using the database
# TODO: Correct the route addresses and method types to match with requirements in assignment description


def store_memcache_statistics():
    with webapp.app_context():
        # TODO: Do some checks/tests to make sure that using the db object in this function while
        # its is being run in a separate thread by the scheduler won't be an issue.
        print(cache.get_statistics()) # Temp for testing locally only
        # stats = CacheStats(**cache.get_statistics())
        # db.session.add(stats)
        # db.session.commit()


@webapp.route('/')
def main():
    return render_template('main.html')


@webapp.route('/get', methods=['POST']) # TODO: This should probably be a GET request not a POST
def get():
    key = request.form.get('key')
    value = cache.get_value(key)

    if value:
        response = webapp.response_class(response=json.dumps(value), status=200,
                                         mimetype='application/json')
    else:
        response = webapp.response_class(response=json.dumps('Unknown key'), status=400,
                                         mimetype='application/json')
    return response


@webapp.route('/put', methods=['POST'])
def put():
    # NOTE: Current assumption is that the received value is a base64 encoded string.
    key = request.form.get('key')
    value = request.form.get('value')

    # TODO: Consider wrapping in a try-except block and defining an error response
    cache.put_item(key, value)
    response = webapp.response_class(response=json.dumps('OK'), status=200,
                                     mimetype='application/json')
    return response


@webapp.route('/clear', methods=['POST'])
def clear():
    # TODO: Consider wrapping in a try-except block and defining an error response
    cache.clear()
    response = webapp.response_class(response=json.dumps('OK'), status=200,
                                     mimetype='application/json')
    return response


@webapp.route('/invalidateKey', methods=['POST'])
def invalidate_key():
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


# @webapp.route('/refreshConfiguration', methods=['POST'])
# def refresh_configuration():
#     # TODO: Consider wrapping in a try-except block and defining an error response
#     config = CacheConfig.query.order_by('updated desc').first_or_404()
#     cache.update_config(config.replacement_policy, config.capacity)
#     response = webapp.response_class(response=json.dumps('OK'), status=200,
#                                      mimetype='application/json')
#     return response
