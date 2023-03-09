from flask import Flask
from app.config_variables import *
global memcache
import boto3
webapp = Flask(__name__)
memcache = {}
s3_client = boto3.client('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    region_name='us-east-1')

s3resource  = boto3.resource('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    region_name='us-east-1')

from app import main
from app import upload
from app import show_image
from app import key_list
from app import api
