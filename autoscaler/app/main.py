import boto3
import logging
import requests

from flask import json, request
from app import webapp, db, scaler
from app.constants import CLOUDWATCH_NAMESPACE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME
from app.autoscaler import ScalingMode
from app.models import CacheStatus

LOG_FORMAT = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
logging.getLogger('apscheduler').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
boto_client = boto3.client('cloudwatch', aws_access_key_id=AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME)


def auto_scale():
    if scaler.mode == ScalingMode.AUTOMATIC:
        # TODO: Actually implement auto scaling logic
        logger.debug(f'AUTO SCALE')
        # data = boto_client.get_metric_data(Namespace=CLOUDWATCH_NAMESPACE)


def activate_node(base_url):
    url = f'{base_url}/activate'
    _ = requests.post(url)


def deactivate_node(base_url):
    url = f'{base_url}/deactivate'
    _ = requests.post(url)


@webapp.route('/automatic', methods=['POST'])
def enable_automatic_mode():
    scaler.set_mode(ScalingMode.AUTOMATIC)

    max_miss_rate = request.form.get('max_miss_rate')
    min_miss_rate = request.form.get('min_miss_rate')
    expand_ratio = request.form.get('expand_ratio')
    shrink_ratio = request.form.get('shrink_ratio')
    scaler.update_config(max_miss_rate, min_miss_rate, expand_ratio, shrink_ratio)

    response = webapp.response_class(response=json.dumps('OK'), status=200,
                                     mimetype='application/json')
    return response


@webapp.route('/manual', methods=['POST'])
def enable_manual_mode():
    scaler.set_mode(ScalingMode.MANUAL)
    response = webapp.response_class(response=json.dumps('OK'), status=200,
                                     mimetype='application/json')
    return response


@webapp.route('/increase_pool', methods=['POST'])
def increase_pool_size():
    if scaler.mode == ScalingMode.MANUAL:
        cache_entry = db.session.query(CacheStatus).filter(CacheStatus.is_active == False).order_by(CacheStatus.id).first()
        if cache_entry:
            logger.info(f'Activating node with id {cache_entry.id}')
            activate_node(cache_entry.base_url)
            response = webapp.response_class(response=json.dumps('OK'), status=200,
                                             mimetype='application/json')
        else:
            response = webapp.response_class(response=json.dumps('No available inactive nodes to be activated'),
                                             status=404, mimetype='application/json')
    else:
        response = webapp.response_class(response=json.dumps('Manual scaling not currently enabled'),
                                         status=405, mimetype='application/json')
    return response


@webapp.route('/decrease_pool', methods=['POST'])
def decrease_pool_size():
    if scaler.mode == ScalingMode.MANUAL:
        cache_entries = db.session.query(CacheStatus).filter(CacheStatus.is_active == True).order_by(CacheStatus.id.desc())
        if cache_entries.count() > 1:
            cache_entry = cache_entries.first()
            logger.info(f'Deactivating node with id {cache_entry.id}')
            deactivate_node(cache_entry.base_url)
            response = webapp.response_class(response=json.dumps('OK'), status=200,
                                             mimetype='application/json')
        else:
            response = webapp.response_class(response=json.dumps('No available active nodes to be deactivated'),
                                             status=404, mimetype='application/json')
    else:
        response = webapp.response_class(response=json.dumps('Manual scaling not currently enabled'),
                                         status=405, mimetype='application/json')
    return response
