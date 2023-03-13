from flask import render_template, url_for, request, g

from app import webapp, memcache, s3_client, s3resource, cloudwatch_client
from flask import json
from PIL import Image, ImageSequence
from pathlib import Path
import io
import base64
import mysql.connector
from app.config_variables import db_config,S3_bucket_name
import os
import glob
from app.config_variables import *

import requests
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from flask import Markup
from datetime import datetime, timedelta
from operator import add


def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_active_nodes():
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SELECT id, is_active FROM cache_status;')
    num_active_nodes = 0
    active_nodes = []
    for row in cursor.fetchall():
        if row[1] == 1:
            num_active_nodes = num_active_nodes + 1
            active_nodes.append(row[0])
    return num_active_nodes, active_nodes

def update_memcache_config(replacement_policy=None, capacity=None):
    if capacity:
        db_con =  get_db()
        cursor= db_con.cursor()
        cursor.execute('UPDATE cache_config SET capacity =  %s WHERE id = %s',(float(capacity),1))
    if replacement_policy:
        db_con =  get_db()
        cursor= db_con.cursor()
        cursor.execute('UPDATE cache_config SET replacement_policy = %s WHERE id = %s',(replacement_policy,1))
    db_con =  get_db()
    cursor= db_con.cursor()
    db_con.commit()

    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SELECT base_url FROM cache_status')
    for row in cursor.fetchall():
        try:
            memcache_refresh_request = requests.post(row[0]+"/refresh_configuration")
            print(row[0] + ": Memcache refresh: "+memcache_refresh_request.text)
        except:
            print("Connection to Mem Cache failed")

def get_cloudwatch_stats(metric, duration):
    """This funciton queries the cloud watch for the metric named <metric>'s average value over the past <duration> minutes, on a per minute interval"""
    (num_active_nodes, active_nodes) = get_active_nodes()
    total_value = []
    for node in active_nodes:
        response = cloudwatch_client.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'testID',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': CLOUDWATCH_NAMESPACE,
                            'MetricName': metric,
                            'Dimensions': [
                                {
                                    'Name': 'ID',
                                    'Value': str(node)
                                },
                            ]
                        },
                        'Period': 1*60,
                        'Stat': 'Average',
                    },
                    'ReturnData': True,
                },
            ],
            StartTime=datetime.utcnow() - timedelta(seconds=duration * 60),
            EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
            ScanBy='TimestampDescending',
        )
        if not total_value:
            total_value = response['MetricDataResults'][0]['Values']
        else:
            total_value = list( map(add, total_value, response['MetricDataResults'][0]['Values']) )
    # need to calculate the average for hit and miss rate
    if metric == 'hit_rate' or metric == 'miss_rate':
        total_value = [x / num_active_nodes for x in total_value]
    return total_value


@webapp.route('/api/getNumNodes', methods=['GET','POST'])
def return_num_active_nodes():
    (num_active_nodes, active_nodes) = get_active_nodes()
    response = webapp.response_class(response=json.dumps({'success': 'true',
                                                              'numNodes': num_active_nodes}), status=200)
    return response

@webapp.route('/api/configure_cache', methods=['GET','POST'])
def cache_configuration():
    mode = request.args.get("mode")
    numNodes = request.args.get("numNodes")
    capacity = request.args.get("cacheSize")
    replacement_policy = request.args.get("policy")
    expRatio = request.args.get("expRatio")
    shrinkRatio = request.args.get("shrinkRatio")
    maxMiss = request.args.get("maxMiss")
    minMiss = request.args.get("minMiss")
    if numNodes:
        numNodes = int(numNodes)
    else:
        numNodes = None
    if capacity:
        capacity = int(capacity)
    else:
        capacity = None
    if expRatio:
        expRatio = float(expRatio)
    else:
        expRatio = None
    if shrinkRatio:
        shrinkRatio = float(shrinkRatio)
    else:
        shrinkRatio = None
    if maxMiss:
        maxMiss = float(maxMiss)
    else:
        maxMiss = None
    if minMiss:
        minMiss = float(minMiss)
    else:
        minMiss = None
    update_memcache_config(replacement_policy, capacity)
    try:
        if mode == "auto":
            requests.post(f'{auto_scaler_base_url}/automatic', data={'max_miss_rate': float(maxMiss),
                                                                    'min_miss_rate': float(minMiss),
                                                                    'expand_ratio': float(expRatio),
                                                                    'shrink_ratio': float(shrinkRatio)})
        elif mode == "manual":
            requests.post(f'{auto_scaler_base_url}/manual')
            (num_active_nodes, active_nodes) = get_active_nodes()
            numNodes = int(numNodes)
            if (numNodes < num_active_nodes):
                difference = num_active_nodes - numNodes
                for i in range(difference):
                    requests.post(f'{auto_scaler_base_url}/decrease_pool')
            elif (numNodes > num_active_nodes):
                difference = numNodes - num_active_nodes
                for i in range(difference):
                    requests.post(f'{auto_scaler_base_url}/increase_pool')
        else:
            # do not update auto scaler if this argument is not given
            pass
    except:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'reason': "Connection to Auto Scaler Failed"}), status=503)
        return response
    response = webapp.response_class(response=json.dumps({'success': 'true',
                                                          'mode': mode,
                                                          'numNodes': numNodes,
                                                          'cacheSize': capacity,
                                                          'policy': replacement_policy}), status=200)
    return response

@webapp.route('/api/delete_all', methods=['GET','POST'])
def delete_everything():
    #Clear database
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SET SQL_SAFE_UPDATES = 0;')
    cursor.execute("DELETE FROM image_key_table1")
    cursor.execute('SET SQL_SAFE_UPDATES = 1;')
    db_con.commit()
    # delete S3 files
    s3resource.Bucket(S3_bucket_name).objects.all().delete()
    #Clear Memcache
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SELECT base_url FROM cache_status')
    for row in cursor.fetchall():
        memcache_clear_request = requests.post(row[0]+"/clear_cache", data={})
        print("Memcache clear: "+memcache_clear_request.text)

    response = webapp.response_class(response=json.dumps({'success': 'true'}), status=200)
    return response

@webapp.route('/api/getRate', methods=['GET','POST'])
def get_cloudwatch_rate():
    rate_type = request.args.get("rate")
    original_rate = rate_type
    if rate_type == 'hit':
        rate_type = 'hit_rate'
    elif rate_type == 'miss':
        rate_type = 'miss_rate'
    else:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'rate': rate_type,
                                                              'reason': "Rate type not supported, the supported options are: hit or miss"}), status=503)
        return response
    stat_list = get_cloudwatch_stats(rate_type, 30)
    last_minute_stat = stat_list[0]
    response = webapp.response_class(response=json.dumps({'success': 'true',
                                                          'rate': original_rate,
                                                          "value": last_minute_stat}), status=200)
    return response


@webapp.route('/api/upload', methods=['POST'])
def route_upload_image():
    try:
        key = request.form.get('key')
        image_file = request.files['file']
        frontend_response = requests.post(f"{frontend_base_url}/upload_image", data={'text': key}, files = {'my_image': image_file})
        response = webapp.response_class(response=json.dumps({'success': 'true',
                                                              'key': key}), status=200)
    except Exception as e:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'error': {'code': 400, 'message': str(e)}}), status=400)
    return response

@webapp.route('/api/list_keys', methods=['POST', 'GET'])
def get_list_of_keys():
    frontend_response = requests.post(f"{frontend_base_url}/api/list_keys")
    data = frontend_response.json()
    response = webapp.response_class(response = json.dumps(data), status=200)
    return response

@webapp.route('/api/key/<key_value>', methods=['POST', 'GET'])
def retrieve_image(key_value):
    frontend_response = requests.post(f"{frontend_base_url}/api/key/{key_value}")
    data = frontend_response.json()
    response = webapp.response_class(response = json.dumps(data), status=200)
    return response