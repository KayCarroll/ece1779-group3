from flask import Flask
from app.config_variables import *
import boto3

global memcache

webapp = Flask(__name__)
memcache = {}
s3_client = boto3.client('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    region_name='us-east-1')

s3resource  = boto3.client('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    region_name='us-east-1')

cloudwatch_client = boto3.client('cloudwatch',
                                 region_name = "us-east-1",
                                 aws_access_key_id=ACCESS_KEY,
                                 aws_secret_access_key=SECRET_KEY)
memcache_option = "manual"

from app import main
from app import memcache_stat
from app import memcache_config
from app import tests
from app import mode_selection

