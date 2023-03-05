
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
    # response = s3_client.upload_file("./tmp/hello.txt", S3_bucket_name, "my_first_upload.txt")
    # print (response)
    metric_data = [{'MetricName': "ID0", 'Value': 20}, {'MetricName': "ID1", 'Value': 15}]
    response = cloudwatch_client.put_metric_data(Namespace='MemCache Metrics', MetricData=metric_data)
    print(response)
    response = cloudwatch_client.list_metrics(Namespace='MemCache Metrics')
    print(response)
    metric_name = 'ID0'
    memcache_metrics = cloudwatch_client.get_metric_statistics(
            Period=1 * 60,
            StartTime=datetime.utcnow() - timedelta(seconds=100 * 60),
            EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
            MetricName=metric_name,
            Statistics=['Sum'],
            Namespace='MemCache Metrics',  # Unit='Percent')
    )
    print(memcache_metrics)
    response = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'testID',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'MemCache Metrics',
                        'MetricName': 'ID0',
                    },
                    'Period': 60,
                    'Stat': 'Average',
                },
                'ReturnData': True,
            },
        ],
        StartTime=datetime.utcnow() - timedelta(seconds=100 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        ScanBy='TimestampDescending',
    )
    print(response)
    return render_template("message.html", user_message = "Updated a metric", return_addr = '/')




