
from flask import render_template, url_for, request, g
from app import webapp, memcache, s3_client, s3resource
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
from app.hashing import *
import app.config_variables
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


@webapp.route('/show_image')
def render_show_image():
    # img_file_path = 'saved_images/dsfsdaf.jpg'
    # im = Image.open(img_file_path)
    # data = io.BytesIO()
    # im.save(data, "JPEG")
    # encoded_img_data = base64.b64encode(data.getvalue())
    popup='0'
  
    
    if app.config_variables.alert=="1":
        app.config_variables.alert="0"
        popup='1'

    return render_template('show_image.html',is_alert=popup)

@webapp.route('/show_image', methods=['POST'])
def show_image():
    # 1. check against database to see if key exist, if not, warn user
    # 2. Check memcache to see if it is in memcache
    # 3. if it does exist, take the data from mem cache, and serve the website
    # 4. if it doesn't exist, take the location provided by database, and load the file
    file_name = request.form.get("text")
    
   
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute("SELECT image_key FROM image_key_table1 WHERE BINARY image_key = BINARY %s GROUP BY image_key",(file_name,))
    exist = cursor.fetchone()

    # check if key exist in database
    if exist is None:
        return render_template('message.html', user_message = "The key you specified does not exist in the database", return_addr='/show_image')

    # check if key exist in mem cache
    
    update_active_list()
    partition_numb=hash_partition(key=file_name)
    active_list_index=route_partition_node(number_active_node=len(active_list),partition_number=partition_numb)
    #print(active_list)
    #print(app.config_variables.active_list)
    
    
    
    url=active_list[active_list_index][1]+"/get_image/"+file_name
    memcache_imagekey_request = requests.get(url)
    
    popup='0'
  
    
    if app.config_variables.alert=="1":
        app.config_variables.alert="0"
        popup='1'

   
    
    #print(image_file)
    if memcache_imagekey_request.json() == 'Unknown key':
        #Load image from local system
        image_file = s3resource.Bucket(S3_bucket_name).Object(file_name).get()
        im = Image.open(image_file['Body'])
        data = io.BytesIO()
        if im.format == "GIF":
            ims = ImageSequence.all_frames(im)
            for img in ims:
                ims[0].save(data, format=im.format, save_all=True, append_images=ims[1:])
        else:
            
            im.save(data, im.format)
        encoded_img_data = base64.b64encode(data.getvalue())
        memcache_updatekey_request = requests.post(active_list[active_list_index][1]+'/cache_image',data={'key': file_name ,'value':encoded_img_data.decode('utf-8')})
        
        print("Memcache" + str(active_list[active_list_index][0]) + " update key value: "+memcache_updatekey_request.text)
        return render_template('show_image.html', format=im.format, img_data = encoded_img_data.decode('utf-8'),is_alert=popup)
    else:
        print("Memcache" + str(active_list[active_list_index][0])+" get image ")
        return render_template('show_image.html', format='', img_data = memcache_imagekey_request.json(),is_alert=popup)
