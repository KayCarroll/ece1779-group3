
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


@webapp.route('/tests')
def tests():
    response = s3_client.upload_file("./tmp/hello.txt", S3_bucket_name, "my_first_upload.txt")
    print (response)
    return render_template("message.html", user_message = "upload is successful if no error pops up", return_addr = '/')




