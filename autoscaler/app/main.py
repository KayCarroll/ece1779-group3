import boto3
import logging
import requests

from datetime import datetime, timedelta
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
        metric_data_queries = [{'Id': 'MISS_RATE_METRICS',
                                'MetricStat': {'Metric': {'Namespace': CLOUDWATCH_NAMESPACE,
                                                          'MetricName': 'miss_rate'},
                                               'Period': 5,
                                               'Stat': 'Average'},
                                'ReturnData': False}]
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=1)
        data_results = boto_client.get_metric_data(MetricDataQueries=metric_data_queries,
                                                   StartTime=start_time, EndTime=end_time)

        # TODO: Figure out if 'values' contains the average miss_rate or a list of all miss_rates
        values = data_results['MetricDataResults'][0]['Values']
        # NOTE: For now, assuming values is a list of miss_rates and not teh average but will need to check this later.
        average_miss_rate = sum(values)/len(values)

        if average_miss_rate > scaler.max_miss_rate:
            # Expand pool
            active_node_count = get_active_node_count()
            target_node_count = active_node_count * scaler.expand_ratio
            for _ in range(target_node_count - active_node_count):
                node_id = activate_node()
                if node_id is None:
                    logger.info('No more available inactive nodes to be activated')
                    break
        elif average_miss_rate < scaler.min_miss_rate:
            # Shrink pool
            active_node_count = get_active_node_count()
            target_node_count = active_node_count * scaler.shrink_ratio
            for _ in range(active_node_count - target_node_count):
                node_id = deactivate_node()
                if node_id is None:
                    logger.info('No more available active nodes to be deactivated')
                    break


def get_active_node_count():
    with webapp.app_context():
        active_node_count = db.session.query(CacheStatus.id).filter(CacheStatus.is_active == True).count()
    return active_node_count


def activate_node():
    with webapp.app_context():
        cache_entry = db.session.query(CacheStatus).filter(CacheStatus.is_active == False).order_by(CacheStatus.id).first()
        if cache_entry:
            logger.info(f'Activating node with id {cache_entry.id}')
            url = f'{cache_entry.base_url}/activate'
            response = requests.post(url)
            logger.debug(f'Node {cache_entry.id} activated with response code {response.status_code}')
            return cache_entry.id
        else:
            return None


def deactivate_node():
    with webapp.app_context():
        cache_entries = db.session.query(CacheStatus).filter(CacheStatus.is_active == True).order_by(CacheStatus.id.desc())
        if cache_entries.count() > 1:
            cache_entry = cache_entries.first()
            logger.info(f'Deactivating node with id {cache_entry.id}')
            url = f'{cache_entry.base_url}/deactivate'
            response = requests.post(url)
            logger.debug(f'Node {cache_entry.id} deactivated with response code {response.status_code}')
            return cache_entry.id
        else:
            return None


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
        node_id = activate_node()
        if node_id is None:
            response = webapp.response_class(response=json.dumps('No available inactive nodes to be activated'),
                                             status=404, mimetype='application/json')
        else:
            response = webapp.response_class(response=json.dumps('OK'), status=200,
                                             mimetype='application/json')
    else:
        response = webapp.response_class(response=json.dumps('Manual scaling not currently enabled'),
                                         status=405, mimetype='application/json')
    return response


@webapp.route('/decrease_pool', methods=['POST'])
def decrease_pool_size():
    if scaler.mode == ScalingMode.MANUAL:
        node_id = deactivate_node()
        if node_id is None:
            response = webapp.response_class(response=json.dumps('No available active nodes to be deactivated'),
                                             status=404, mimetype='application/json')
        else:
            response = webapp.response_class(response=json.dumps('OK'), status=200,
                                             mimetype='application/json')
    else:
        response = webapp.response_class(response=json.dumps('Manual scaling not currently enabled'),
                                         status=405, mimetype='application/json')
    return response