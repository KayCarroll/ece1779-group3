
from flask import render_template, url_for, request, g
from app import webapp, memcache, s3_client, cloudwatch_client
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
from datetime import datetime, timedelta

import boto3


@webapp.route('/tests')
def tests():
    files = {'file': open('tmp/test.txt', 'rb')}
    values = {'key': 'def.txt'}
    r = requests.post(f'{manager_base_url}/api/upload', files=files, data=values)
    print(r)
    return render_template("message.html", user_message = str(r.content), return_addr = '/')




