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
        requests.post(f'{manager_base_url}/api/delete_all')
        return render_template("message.html", user_message = "All application data is deleted", return_addr = "config")
    elif "clear_memcache" in request.form:
        db_con =  get_db()
        cursor= db_con.cursor()
        cursor.execute('SELECT base_url FROM cache_status')
        for row in cursor.fetchall():

            memcache_clear_request = requests.post(row[0]+"/clear_cache", data={})
            print("Memcache clear: "+memcache_clear_request.text)


        return render_template("message.html", user_message = "MemCache cleared", return_addr = "config")

    cache_size = request.form.get("cache_size")
    option_selected = request.form.get("policyRadios")
    response = requests.post(f'{manager_base_url}/api/configure_cache?cacheSize={cache_size}&policy={option_selected}')
    return_status = response.status_code
    if (return_status == 200):
        return render_template("message.html", user_message = "MemCache Config Update Success", return_addr = "config")
    else:
        return render_template("message.html", user_message = "MemCache Config Update Failed", return_addr = "config")
