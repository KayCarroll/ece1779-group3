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

@webapp.route('/config')
def config():
    return render_template("config.html")

@webapp.route('/config', methods=['POST'])
def process_config():
    print(request.form)
    if 'display' in request.form:
        # TODO: contact mem cache to get the list of keys
        memcache_getkeys_request = requests.get("http://localhost:5001/get_lru_keys")
        print("Memcache Get kes: ")
        print(memcache_getkeys_request.json())
        mecmcache_key_list = memcache_getkeys_request.json()
        return render_template("show_list.html", list_title='All Keys In MemCache', input_list=mecmcache_key_list, return_addr='/config')
    elif 'clear' in request.form:
        #send the clear message to mem cache
        memcache_clear_request = requests.post("http://localhost:5001/clear_cache", data={})
        print("Memcache clear: "+memcache_clear_request.text)
        return render_template("config.html", message = "Cache Cleared!")
    cache_size = request.form.get("cache_size")
    cache_size_float = float(cache_size)
    print(cache_size)

    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('UPDATE cache_config SET capacity =  %s WHERE id = %s',(cache_size,1))
    # the option_selected has 2 possible values (both string): RR and LRU
    option_selected = request.form.get("policyRadios")
    print(option_selected)
    cursor.execute('UPDATE cache_config SET replacement_policy = %s WHERE id = %s',(option_selected,1))
    db_con.commit()
    # TODO: write the options to database and call refreshConfiguration() for memcache

    memcache_refresh_request = requests.post("http://localhost:5001/refresh_configuration")

    print("Memcache refresh: "+memcache_refresh_request.text)

    return render_template("config.html")aded successfully!", return_addr='/upload_image')