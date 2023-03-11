from flask import render_template, url_for, request, g
from app import webapp, memcache, s3_client
from flask import json
from PIL import Image, ImageSequence
from pathlib import Path
import io
import base64
import mysql.connector
from app.config_variables import *
from app.api import get_active_nodes
import os
import glob
from app.api import get_cloudwatch_stats

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


@webapp.route('/statistics')
def statistics():
    # TODO: Contact Database to read statistics
    # db_con =  get_db()
    # cursor= db_con.cursor()
    # cursor.execute('SELECT * FROM ( SELECT * FROM cache_stats ORDER BY id DESC LIMIT %s) AS sub ORDER BY id ASC',(121,))
    # cache_count=[]
    # cache_size=[]
    # miss_rate=[]
    # hit_rate=[]
    # requests_served=[]
    # for row in cursor.fetchall():
    #     cache_count.append(row[2])
    #     cache_size.append(row[3])
    #     miss_rate.append(row[4])
    #     hit_rate.append(row[5])
    #     requests_served.append(row[6])

    # TODO: find number of active nodes and gather cloudwatch data
    (num_active_nodes, active_node_ID) = get_active_nodes()
    statistics = {
        "cache_count": [],
        "cache_size": [],
        "miss_rate": [],
        "hit_rate": [],
        "requests_served": [],
    }
    metrices = list(statistics.keys())
    for metric in metrices:
        statistics[metric] = get_cloudwatch_stats(metric, 30)

    x_axis = list(range(30, 0, -1))
    cache_count_plot = plot({"data":go.Scatter(x=x_axis, y=statistics['cache_count']), "layout": go.Layout(title = "Cache Count", xaxis_title = "Time(min)",yaxis_title = "Items in Cache")},output_type='div')
    cache_size_plot = plot({"data":go.Scatter(x=x_axis, y=statistics['cache_size']), "layout": go.Layout(title = "Cache Size", xaxis_title = "Time(min)",yaxis_title = "MB")},output_type='div')
    miss_rate_plot = plot({"data":go.Scatter(x=x_axis, y=statistics['miss_rate']), "layout": go.Layout(title = "Miss Rate", xaxis_title = "Time(min)",yaxis_title = "Rate")},output_type='div')
    hit_rate_plot = plot({"data":go.Scatter(x=x_axis, y=statistics['hit_rate']), "layout": go.Layout(title = "Hit Rate", xaxis_title = "Time(min)",yaxis_title = "Rate")},output_type='div')
    requests_served_plot = plot({"data":go.Scatter(x=x_axis, y=statistics['requests_served']), "layout": go.Layout(title = "Requests Served", xaxis_title = "Time(min)",yaxis_title = "Number of Request")},output_type='div')

    plot_list = ["Number of Active Nodes: " + str(num_active_nodes), "Active Nodes: " + str(active_node_ID), Markup(cache_count_plot),Markup(cache_size_plot),Markup(miss_rate_plot),Markup(hit_rate_plot),Markup(requests_served_plot)]
    return render_template("show_list.html", list_title='MemCache Statistics', input_list=plot_list, return_addr='/')
