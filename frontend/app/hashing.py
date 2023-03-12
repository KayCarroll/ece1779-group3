# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 22:40:07 2023

@author: Sam
"""

import hashlib

from flask import render_template, url_for, request, g
from app import webapp, memcache, s3_client, s3resource
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

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



partition_list = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'a':10,'b':11,'c':12,'d':13,'e':14,'f':15}


#active_list=['a','b','c','d']


def hash_partition(key='k1'):
    hashed_key= hashlib.md5(key.encode()).hexdigest()



    
    return partition_list[hashed_key[0].lower()]


def route_partition_node(number_active_node=1,partition_number=0):
    
    return partition_number%number_active_node

def update_active_list():
    global active_list
    
    active_list.clear()
    
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SELECT * FROM cache_status')
    for row in cursor.fetchall():
        if row[1]==1:
            active_list.append((row[0],row[2]))
        
    
    
    
    
 


 
#list_key=['k1','k2','k3','k4','k5','k6']    


#for key in list_key:
 #   part_number=hash_partition(key=key)
  #  print(part_number)
   # print(key, " Belong to partion ",part_number+1)
    #print("Belong to node: ",active_list[route_partition_node(number_active_node=len(active_list),partition_number=part_number)])





#print(hashed_key, " Belong to partion ",partition_list[hashed_key[0].lower()]+1)





#print(hashed_key2, " Belong to partion ",partition_list[hashed_key2[0].lower()]+1)
#print((int)hashed_key%16)