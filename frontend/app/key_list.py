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

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route('/available_keys')
def available_keys():
    # Contact database to get a list of keys
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute("SELECT * FROM image_key_table1")
    database_key_list = [row[0] for row in cursor.fetchall()]
    return render_template("show_keylist.html",list_title='All Available Keys', input_list=database_key_list, return_addr='/')

@webapp.route('/available_keys',methods=['POST'])
def key_deletion():
    #Clear database
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SET SQL_SAFE_UPDATES = 0;')
    cursor.execute("DELETE FROM image_key_table1")
    cursor.execute('SET SQL_SAFE_UPDATES = 1;')
    db_con.commit()
    #Clear local system
    images = glob.glob('saved_images/*')
    for im in images:
        os.remove(im)

    #Clear Memcache
    memcache_clear_request = requests.post("http://localhost:5001/clear_cache", data={})
    print("Memcache clear: "+memcache_clear_request.text)

    return available_keys()