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
from app.api import get_active_nodes

import requests
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from flask import Markup

import boto3

@webapp.route('/mode_selection')
def mode_selection():
    global memcache_option
    (num_active_nodes, active_nodes) = get_active_nodes()
    if memcache_option == "manual":
        return render_template("manual_mode.html", active_no = num_active_nodes)
    elif memcache_option == "automatic":
        return render_template("automatic_mode.html")
    else:
        memcache_option = "manual"
        return render_template("manual_mode.html", active_no = num_active_nodes)

@webapp.route('/mode_selection', methods=['POST'])
def handle_mode_form_submit():
    global memcache_option
    if 'switch_to_automatic' in request.form:
        # only available in manual mode
        memcache_option = "automatic"
        try:
            requests.post(f'{auto_scaler_base_url}/automatic')
        except:
            return render_template("message.html", user_message = "Connection to auto scaler failed", return_addr = "mode_selection")
        return mode_selection()
    elif 'switch_to_manual' in request.form:
        # only available in automatic mode
        memcache_option = "manual"
        try:
            requests.post(f'{auto_scaler_base_url}/manual')
        except:
            return render_template("message.html", user_message = "Connection to auto scaler failed", return_addr = "mode_selection")
        return mode_selection()
    elif 'increase_capacity' in request.form:
        # only available in manual mode
        try:
            requests.post(f'{auto_scaler_base_url}/increase_pool')
        except:
            return render_template("message.html", user_message = "Connection to auto scaler failed", return_addr = "mode_selection")
        return mode_selection()
    elif 'decrease_capacity' in request.form:
        # only available in manual mode
        try:
            requests.post(f'{auto_scaler_base_url}/decrease_pool')
        except:
            return render_template("message.html", user_message = "Connection to auto scaler failed", return_addr = "mode_selection")
        return mode_selection()

    max_miss_rate = float(request.form.get("max_miss_rate"))/100
    min_miss_rate = float(request.form.get("min_miss_rate"))/100
    expand_ratio = float(request.form.get("expand_ratio"))
    shrink_ratio = float(request.form.get("shrink_ratio"))
    mode = ""
    if memcache_option == "automatic":
        mode = "auto"
    else:
        mode = "manual"
    try:
        requests.post(f'{manager_base_url}/api/configure_cache?mode={mode}&expRatio={expand_ratio}&shrinkRatio={shrink_ratio}&maxMiss={max_miss_rate}&minMiss={min_miss_rate}')
    except:
        return render_template("message.html", user_message = "Connection to auto scaler failed", return_addr = "mode_selection")
    return mode_selection()