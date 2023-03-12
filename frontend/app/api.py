from flask import render_template, url_for, request, g
from app import webapp, memcache
from flask import json
from PIL import Image, ImageSequence
from pathlib import Path
import io
import base64
import mysql.connector
from app.config_variables import *
import os
import glob

import requests
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from flask import Markup
from app.hashing import *
import boto3


#CACHE_API_BASE_URL = 'http://localhost:5001'
IMAGE_DIR = 'saved_images'
TABLE_NAME = 'image_key_table1'

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


S3_bucket_name = 'ece1779samwang-a2'
@webapp.route('/api/delete_all', methods=['POST'])
def delete_all():
    try:
        #Clear database
        db_con =  get_db()
        cursor= db_con.cursor()
        cursor.execute('SET SQL_SAFE_UPDATES = 0;')
        cursor.execute("DELETE FROM image_key_table1")
        cursor.execute('SET SQL_SAFE_UPDATES = 1;')
        db_con.commit()
        #Clear local system
        # delete the file



        s3resource.Bucket(S3_bucket_name).objects.all().delete()
        #Clear Memcache
    
        db_con =  get_db()
        cursor= db_con.cursor()
        cursor.execute('SELECT base_url FROM cache_status')
        for row in cursor.fetchall():
        
            memcache_clear_request = requests.post(row[0]+"/clear_cache", data={})

        response = webapp.response_class(response=json.dumps({'success': 'true'}), status=200)
    except Exception as e:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'error': {'code': 400, 'message': str(e)}}), status=400)
    return response


@webapp.route('/api/upload', methods=['POST'])
def upload():
    try:
        key = request.form.get('key')
        image_file = request.files['file']

        db_con =  get_db()
        cursor= db_con.cursor()
        #Check the key is not duplicate, if it is, replace the old file
        cursor.execute("SELECT image_key FROM image_key_table1 WHERE BINARY image_key = BINARY %s GROUP BY image_key",(key,))
        exist = cursor.fetchone()
        # add the key to the list of known keys in the database
        if exist is None:
            cursor.execute("INSERT INTO image_key_table1 VALUES(%s)",(key,))
            db_con.commit()
            
        s3_client.upload_fileobj(image_file, S3_bucket_name, key)
        update_active_list()
        partition_numb=hash_partition(key=key)
        active_list_index=route_partition_node(number_active_node=len(active_list),partition_number=partition_numb)
        memcache_invalidate_request = requests.post(active_list[active_list_index][1]+"/invalidate_key", data={'key': key })
        response = webapp.response_class(response=json.dumps({'success': 'true',
                                                              'key': key}), status=200)
    except Exception as e:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'error': {'code': 400, 'message': str(e)}}), status=400)
    return response


@webapp.route('/api/list_keys', methods=['POST'])
def list_keys():
    try:
        db_con =  get_db()
        cursor= db_con.cursor()
        cursor.execute(f'SELECT * FROM {TABLE_NAME}')
        database_key_list = [row[0] for row in cursor.fetchall()]

        response = webapp.response_class(response=json.dumps({'success': 'true',
                                                              'keys': database_key_list}), status=200)
    except Exception as e:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'error': {'code': 400, 'message': str(e)}}), status=400)
    return response


@webapp.route('/api/key/<key_value>', methods=['POST'])
def get_image(key_value):
    try:
        # check if key exist in mem cache
        
        update_active_list()
        partition_numb=hash_partition(key=key_value)
        active_list_index=route_partition_node(number_active_node=len(active_list),partition_number=partition_numb)
        
        
        
        url=active_list[active_list_index][1]+"/get_image/"+key_value
        cache_response = requests.get(url)
        
      
        if cache_response.status_code == 200:
            image_str = cache_response.json()
        else:
 
            
            
            #Load image from local system
            image_file = s3resource.Bucket(S3_bucket_name).Object(key_value).get()
            im = Image.open(image_file['Body'])
            data = io.BytesIO()
            if im.format is "GIF":
                ims = ImageSequence.all_frames(im)
                for img in ims:
                    ims[0].save(data, format=im.format, save_all=True, append_images=ims[1:])
            else:
                
                im.save(data, im.format)
            image_str = base64.b64encode(data.getvalue())

            cache_response = requests.post(f'{CACHE_API_BASE_URL}/cache_image',
                                           data={'key': key_value ,'value': image_str.decode('utf-8')})

        response = webapp.response_class(response=json.dumps({'success': 'true', 'key': key_value,
                                                              'content': image_str.decode('utf-8')}), status=200)
    except Exception as e:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'error': {'code': 400, 'message': str(e)}}), status=400)
    return response
