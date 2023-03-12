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

@webapp.route('/pool_changes')
def pool_changes():
    # Contact database to get a list of keys
    active_count=0
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SELECT * FROM cache_status')
    for row in cursor.fetchall():
        if row[1]==1:
            active_count=active_count+1
    global before_active       
    return render_template("show_nodes_changes.html",before_active =before_active, current_active=str(active_count) , return_addr='/')

