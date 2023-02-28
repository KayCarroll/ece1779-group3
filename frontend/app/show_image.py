
from flask import render_template, url_for, request, g
from app import webapp, memcache
from flask import json
from PIL import Image, ImageSequence
from pathlib import Path
import io
import base64
import mysql.connector
from app.config import db_config
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


@webapp.route('/show_image')
def render_show_image():
    # img_file_path = 'saved_images/dsfsdaf.jpg'
    # im = Image.open(img_file_path)
    # data = io.BytesIO()
    # im.save(data, "JPEG")
    # encoded_img_data = base64.b64encode(data.getvalue())
    return render_template('show_image.html')

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
    url="http://localhost:5001/get_image/"+file_name
    memcache_imagekey_request = requests.get(url)
    print("Memcache get image: "+memcache_imagekey_request.json())

    #Load image from local system
    if memcache_imagekey_request.json() == 'Unknown key':

        img_file_path = "saved_images/" + file_name
        path = Path(img_file_path)
        im = Image.open(img_file_path)
        data = io.BytesIO()
        if im.format is "GIF":
            ims = ImageSequence.all_frames(im)
            for img in ims:
                ims[0].save(data, format=im.format, save_all=True, append_images=ims[1:])
        else:
            im.save(data, im.format)
        encoded_img_data = base64.b64encode(data.getvalue())


        #Put Key and image into memcache
        memcache_updatekey_request = requests.post('http://localhost:5001/cache_image',data={'key': file_name ,'value':encoded_img_data.decode('utf-8')})
        print("Memcache update key value: "+memcache_updatekey_request.text)

        return render_template('show_image.html', format=im.format, img_data = encoded_img_data.decode('utf-8'))
    else:
        return render_template('show_image.html', format='', img_data = memcache_imagekey_request.json())