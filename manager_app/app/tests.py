
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
    test_4_flag = True
    score = 0
    try:
        response = requests.post(manager_base_url + "/api/key/test_1")
    except:
        print("error in test 4: could not post /key/test_1 to your web app")
        print("check the web app connection, IP, port, API endpoint path, etc.")
        test_4_flag = False

    if test_4_flag:
        try:
            jsonResponse = response.json()
        except:
            print("error in test 4: your response cannot be represented in JSON format")
        try:
            # print ("Success field: " + jsonResponse["success"])
            # print ("key field: " + jsonResponse["key"])
            # print ("content field: " + jsonResponse["content"])
            if jsonResponse["success"] == "true":
                print("success pass")
            if jsonResponse["key"] == "test_1":
                print("key pass")
            if (jsonResponse["content"] != None):
                print("Content pass")
            if jsonResponse["success"] == "true" and jsonResponse["key"] == "test_1" and jsonResponse["content"] != None:
                score += 1
            else:
                print("""error in test 4: /key/test_1 operation should return 
                        {
                            "success": "true", 
                            "key" : "test_1",
                            "content" : file contents
                        }""")
                print("your response: ")
                print(jsonResponse)
                print("")
        except:
            print('error in test 4: access failure on ["success"]/["key"]/["content"] of the post response')
            print("")
    return render_template("message.html", user_message = str("ok"), return_addr = '/')




