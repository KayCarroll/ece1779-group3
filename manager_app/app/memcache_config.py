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

@webapp.route('/config')
def config():
    return render_template("config.html")

@webapp.route('/config', methods=['POST'])
def process_config():
    if "delete_all" in request.form:
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
        memcache_clear_request = requests.post("http://localhost:5001/clear_cache", data={})
        print("Memcache clear: "+memcache_clear_request.text)
        
        return render_template("message.html", user_message = "All application data is deleted", return_addr = "config")
    elif "clear_memcache" in request.form:
        return render_template("message.html", user_message = "MemCache cleared", return_addr = "config")
    cache_size = request.form.get("cache_size")
    cache_size_float = float(cache_size)
    print(cache_size)
    # TODO: Update cache size for all 8 nodes
    # the option_selected has 2 possible values (both string): RR and LRU
    option_selected = request.form.get("policyRadios")
    print(option_selected)
    # TODO: write the options to database and call refreshConfiguration() for memcache
    return render_template("config.html")