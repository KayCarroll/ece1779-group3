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

import requests
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from flask import Markup


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
    active_nodes = 0
    for row in cursor.fetchall():
        if row[1] == 1:
            active_nodes = active_nodes + 1
    return active_nodes

def update_memcache_config(replacement_policy=None, capacity=None):
    print("capacity is: " + capacity)
    if capacity:
        db_con =  get_db()
        cursor= db_con.cursor()
        print('UPDATE cache_config SET capacity =  %s WHERE id = %s',(float(capacity),1))
        cursor.execute('UPDATE cache_config SET capacity =  %s WHERE id = %s',(float(capacity),1))
    if replacement_policy:
        db_con =  get_db()
        cursor= db_con.cursor()
        cursor.execute('UPDATE cache_config SET replacement_policy = %s WHERE id = %s',(replacement_policy,1))
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('UPDATE cache_config SET capacity =  %s WHERE id = %s',(float(capacity),1))
    cursor.execute('UPDATE cache_config SET replacement_policy = %s WHERE id = %s',(replacement_policy,1))
    db_con.commit()

    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SELECT base_url FROM cache_status')
    for row in cursor.fetchall():
        memcache_refresh_request = requests.post(row[0]+"/refresh_configuration")
        print(row[0] + ": Memcache refresh: "+memcache_refresh_request.text)

@webapp.route('/api/getNumNodes')
def return_num_active_nodes():
    active_nodes = get_active_nodes()
    response = webapp.response_class(response=json.dumps({'success': 'true',
                                                              'numNodes': active_nodes}), status=200)
    return response

@webapp.route('/api/configure_cache', methods=['GET','POST'])
def cache_configuration():
    mode = request.args.get("mode")
    numNodes = request.args.get("numNodes")
    if numNodes:
        numNodes = int(numNodes)
    capacity = request.args.get("cacheSize")
    replacement_policy = request.args.get("policy")
    expRatio = request.args.get("expRatio")
    shrinkRatio = request.args.get("shrinkRatio")
    maxMiss = request.args.get("maxMiss")
    minMiss = request.args.get("minMiss")
    print ("INSIDE API")
    print(capacity)
    print(replacement_policy)
    update_memcache_config(replacement_policy, capacity)
    # TODO: Update auto scaler
    response = webapp.response_class(response=json.dumps({'success': 'true',
                                                          'mode': mode,
                                                          'numNodes': numNodes,
                                                          'cacheSize': int(capacity),
                                                          'policy': replacement_policy}), status=200)
    return response
