
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
    my_dict = {'cache_id': 2, 'is_active': int(True), 'cache_count': 15,
                'cache_size': 32, 'hit_rate': 0.8, 'miss_rate': 0.2,
                'requests_served': 46}
    instance_id = "2"
    # metric_data = [
    #     {
    #         'MetricName': "hit_rate",
    #         'Dimensions': [
    #             {
    #                 'Name': 'ID',
    #                 'Value': '0'
    #             },
    #         ],
    #         'Value': 0.6
    #     },
    #     {
    #         'MetricName': "hit_rate",
    #         'Dimensions': [
    #             {
    #                 'Name': 'ID',
    #                 'Value': '1'
    #             },
    #         ],
    #         'Value': 0.2
    #     }
    # ]
    metric_data = [{'MetricName': key, 'Dimensions': [{'Name': 'ID', 'Value': instance_id}], 'Value': val} for key, val in my_dict.items()]
    response = cloudwatch_client.put_metric_data(Namespace='MemCache Metrics', MetricData=metric_data)
    print(response)
    response = cloudwatch_client.list_metrics(Namespace='MemCache Metrics')
    print(response)
    response = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'testID',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'MemCache Metrics',
                        'MetricName': 'hit_rate',
                        'Dimensions': [
                            {
                                'Name': 'ID',
                                'Value': '2'
                            },
                        ]
                    },
                    'Period': 1*60,
                    'Stat': 'Average',
                },
                'ReturnData': True,
            },
        ],
        StartTime=datetime.utcnow() - timedelta(seconds=200 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        ScanBy='TimestampAscending',
    )
    print(response)
    return render_template("message.html", user_message = "Updated a metric", return_addr = '/')




