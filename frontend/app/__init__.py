from flask import Flask

global memcache

webapp = Flask(__name__)
memcache = {}

from app import main
from app import upload
from app import show_image
from app import key_list
from app import api
