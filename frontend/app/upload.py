from flask import render_template, url_for, request, g
from app import webapp, memcache, s3_client, s3resource
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



@webapp.route('/upload_image')
def render_upload_image():
    return render_template("upload.html")

@webapp.route('/upload_image', methods=['POST'])
def upload_image():
    file_name = request.form.get("text")
    
    
    db_con =  get_db()
    cursor= db_con.cursor()
    #Check the key is not duplicate, if it is, replace the old file
    cursor.execute("SELECT image_key FROM image_key_table1 WHERE BINARY image_key = BINARY %s GROUP BY image_key",(file_name,))
    exist = cursor.fetchone()
    # add the key to the list of known keys in the database
    if exist is None:
        cursor.execute("INSERT INTO image_key_table1 VALUES(%s)",(file_name,))
        db_con.commit()
        
   
    file = request.files['my_image']
 
    #print (file)
    #print(file.content_type)
   # print(file.filename)
    #print(file.mimetype)
    #print(file.name)


    s3_client.upload_fileobj(file, S3_bucket_name, file_name)
    
    update_active_list()
 


    #invalidate memcache key
    partition_numb=hash_partition(key=file_name)

    active_list_index=route_partition_node(number_active_node=len(active_list),partition_number=partition_numb)

    memcache_invalidate_request = requests.post(active_list[active_list_index][1]+"/invalidate_key", data={'key': file_name })
 

    #print("Memcache invaldte: "+memcache_invalidate_request.text)

    return render_template('message.html', user_message = "Your image has been uploaded successfully!", return_addr='/upload_image')