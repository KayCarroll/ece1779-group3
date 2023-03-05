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

@webapp.route('/mode_selection')
def mode_selection():
    global memcache_option
    # TODO: Get number of active nodes if it's manual mode
    if memcache_option == "manual":
        return render_template("manual_mode.html", active_no = 3)
    elif memcache_option == "automatic":
        return render_template("automatic_mode.html")
    else:
        memcache_option = "manual"
        return render_template("manual_mode.html", active_no = 3)

@webapp.route('/mode_selection', methods=['POST'])
def handle_mode_form_submit():
    global memcache_option
    if 'switch_to_automatic' in request.form:
        # only available in manual mode
        memcache_option = "automatic"
        return mode_selection()
    elif 'switch_to_manual' in request.form:
        # only available in automatic mode
        memcache_option = "manual"
        return mode_selection()
    # TODO: ask auto scaler to increase/decrease nodes
    elif 'increase_capacity' in request.form:
        # only available in manual mode
        return mode_selection()
    elif 'decrease_capacity' in request.form:
        # only available in manual mode
        return mode_selection()
    max_miss_rate = float(request.form.get("max_miss_rate"))/100
    min_miss_rate = float(request.form.get("min_miss_rate"))/100
    expand_ratio = float(request.form.get("expand_ratio"))
    shrink_ratio = float(request.form.get("shrink_ratio"))
    print("max miss rate, min miss rate, expand ratio, shrink ratio: ", max_miss_rate, " ", min_miss_rate, " ", expand_ratio, " ", shrink_ratio)
    # TODO: Send this info to auto scaler
    return mode_selection()