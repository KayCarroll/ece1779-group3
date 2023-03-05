from flask import render_template, url_for, request, g
from app import webapp, memcache, s3_client
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
    active_node_ID = [0, 1, 3, 4, 7]
    inactive_node_ID = [2, 5, 6]
    number_of_active_nodes = [1, 3, 4, 4, 5]
    cache_count=[3, 4, 7, 12, 15]
    cache_size=[4.3, 5.3, 7.2, 17.4, 22.1]
    miss_rate=[0.9, 0.2, 0.3, 0.15, 0.1]
    hit_rate=[0.1, 0.8, 0.7, 0.85, 0.9]
    requests_served=[21, 43, 10, 0, 30]

    x_axis = list(range(0, 30, 1))
    active_nodes_plot = plot({"data":go.Scatter(x=x_axis, y=number_of_active_nodes), "layout": go.Layout(title = "Active Nodes", xaxis_title = "Time(min)",yaxis_title = "Number of Active Nodes")},output_type='div')
    cache_count_plot = plot({"data":go.Scatter(x=x_axis, y=cache_count), "layout": go.Layout(title = "Cache Count", xaxis_title = "Time(min)",yaxis_title = "Number of Cache")},output_type='div')
    cache_size_plot = plot({"data":go.Scatter(x=x_axis, y=cache_size), "layout": go.Layout(title = "Cache Size", xaxis_title = "Time(min)",yaxis_title = "MB")},output_type='div')
    miss_rate_plot = plot({"data":go.Scatter(x=x_axis, y=miss_rate), "layout": go.Layout(title = "Miss Rate", xaxis_title = "Time(min)",yaxis_title = "Rate")},output_type='div')
    hit_rate_plot = plot({"data":go.Scatter(x=x_axis, y=hit_rate), "layout": go.Layout(title = "Hit Rate", xaxis_title = "Time(min)",yaxis_title = "Rate")},output_type='div')
    requests_served_plot = plot({"data":go.Scatter(x=x_axis, y=requests_served), "layout": go.Layout(title = "Requests Served", xaxis_title = "Time(min)",yaxis_title = "Number of Request")},output_type='div')

    plot_list = ["Active Nodes: " + str(active_node_ID), "Inactive Nodes: " + str(inactive_node_ID), Markup(active_nodes_plot), Markup(cache_count_plot),Markup(cache_size_plot),Markup(miss_rate_plot),Markup(hit_rate_plot),Markup(requests_served_plot)]
    return render_template("show_list.html", list_title='MemCache Statistics', input_list=plot_list, return_addr='/')
