
from flask import render_template, url_for, request, g
from app import webapp, memcache
from flask import json
from PIL import Image, ImageSequence
from pathlib import Path
import io
import base64
import mysql.connector
import app.config_variables
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

@webapp.route('/')
def main():
    return render_template("main.html")

@webapp.route('/navbar')
def global_navbar():
    return render_template("navbar.html")

@webapp.route('/get',methods=['POST'])
def get():
    key = request.form.get('key')

    if key in memcache:
        value = memcache[key]
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Unknown key"),
            status=400,
            mimetype='application/json'
        )

    return response

@webapp.route('/put',methods=['POST'])
def put():
    key = request.form.get('key')
    value = request.form.get('value')
    memcache[key] = value

    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )

    return response

@webapp.route('/nodeupdate', methods=['POST','GET'])
def node_update():
    """update the cache node.
    """
    
    current_key_in_node = []
    global before_active 
    print(before_active)
    before_active=str(len(active_list))
    
    for index, uri in active_list:
        memcache_getkeys_request = requests.get(uri+"/get_lru_keys")
        print("Memcache Get kes: ")
        print(memcache_getkeys_request.json())
        mecmcache_key_list = memcache_getkeys_request.json()
        current_key_in_node=current_key_in_node+mecmcache_key_list
        memcache_clear_request = requests.post(uri+"/clear_cache", data={})

        
    update_active_list()

    
    for file_name in current_key_in_node:
        partition_numb=hash_partition(key=file_name)
        active_list_index=route_partition_node(number_active_node=len(active_list),partition_number=partition_numb)
        image_file = s3resource.Bucket(S3_bucket_name).Object(file_name).get()
        im = Image.open(image_file['Body'])
        data = io.BytesIO()
        if im.format is "GIF":
            ims = ImageSequence.all_frames(im)
            for img in ims:
                ims[0].save(data, format=im.format, save_all=True, append_images=ims[1:])
        else:
            
            im.save(data, im.format)
        encoded_img_data = base64.b64encode(data.getvalue())
        memcache_updatekey_request = requests.post(active_list[active_list_index][1]+'/cache_image',data={'key': file_name ,'value':encoded_img_data.decode('utf-8')})
        print("Memcache update key value: "+memcache_updatekey_request.text)

    print("End point before ")
    print(app.config_variables.alert)
    app.config_variables.alert='1'
    print(app.config_variables.alert)
    response = webapp.response_class(response=json.dumps('OK'), status=200,
                                     mimetype='application/json')
    return response
