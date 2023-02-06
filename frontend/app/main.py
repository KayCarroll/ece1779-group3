
from flask import render_template, url_for, request, g
from app import webapp, memcache
from flask import json
from PIL import Image, ImageSequence
from pathlib import Path
import io
import base64
import mysql.connector
from app.config import db_config
import os
import glob

import requests
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from flask import Markup

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

@webapp.route('/')
def main():
    return render_template("main.html")

@webapp.route('/upload_image')
def render_upload_image():
    return render_template("upload.html")

@webapp.route('/upload_image', methods=['POST'])
def upload_image():
    file_name = request.form.get("text")
    db_con =  get_db()
    cursor= db_con.cursor()
    #Check the key is not duplicate, if it is, replace the old file
    cursor.execute("SELECT image_key FROM image_key_table1 WHERE BINARY image_key = BINARY %s GROUP BY image_key",(file_name,))
    exist = cursor.fetchone()
    # add the key to the list of known keys in the database
    if exist is None:
        cursor.execute("INSERT INTO image_key_table1 VALUES(%s)",(file_name,))
        db_con.commit()
    file = request.files['my_image']
    print (file)
    print(file.content_type)
    print(file.filename)
    print(file.mimetype)
    print(file.name)
    file_path = "saved_images/" + file_name
    isExist = os.path.exists("saved_images")
    if not isExist:
        os.makedirs("saved_images")
        print("Saved images directory is created!")
    file.save(file_path)

    #invalidate memcache key
    memcache_invalidate_request = requests.post("http://localhost:5001/invalidate_key", data={'key': file_name })
 

    print("Memcache invaldte: "+memcache_invalidate_request.text)

    return render_template('message.html', user_message = "Your image has been uploaded successfully!", return_addr='/upload_image')

@webapp.route('/show_image')
def render_show_image():
    # img_file_path = 'saved_images/dsfsdaf.jpg'
    # im = Image.open(img_file_path)
    # data = io.BytesIO()
    # im.save(data, "JPEG")
    # encoded_img_data = base64.b64encode(data.getvalue())
    return render_template('show_image.html')

@webapp.route('/show_image', methods=['POST'])
def show_image():
    # 1. check against database to see if key exist, if not, warn user
    # 2. Check memcache to see if it is in memcache
    # 3. if it does exist, take the data from mem cache, and serve the website
    # 4. if it doesn't exist, take the location provided by database, and load the file
    file_name = request.form.get("text")
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute("SELECT image_key FROM image_key_table1 WHERE BINARY image_key = BINARY %s GROUP BY image_key",(file_name,))
    exist = cursor.fetchone()

    # check if key exist in database
    if exist is None:
        return render_template('message.html', user_message = "The key you specified does not exist in the database", return_addr='/show_image')

    # check if key exist in mem cache
    url="http://localhost:5001/get_image/"+file_name
    memcache_imagekey_request = requests.get(url)
    print("Memcache get image: "+memcache_imagekey_request.json())

    #Load image from local system
    if memcache_imagekey_request.json() == 'Unknown key':

        img_file_path = "saved_images/" + file_name
        path = Path(img_file_path)
        im = Image.open(img_file_path)
        data = io.BytesIO()
        if im.format is "GIF":
            ims = ImageSequence.all_frames(im)
            for img in ims:
                ims[0].save(data, format=im.format, save_all=True, append_images=ims[1:])
        else:
            im.save(data, im.format)
        encoded_img_data = base64.b64encode(data.getvalue())


        #Put Key and image into memcache
        memcache_updatekey_request = requests.post('http://localhost:5001/cache_image',data={'key': file_name ,'value':encoded_img_data.decode('utf-8')})
        print("Memcache update key value: "+memcache_updatekey_request.text)

        return render_template('show_image.html', format=im.format, img_data = encoded_img_data.decode('utf-8'))
    else:
        return render_template('show_image.html', format='', img_data = memcache_imagekey_request.json())


@webapp.route('/available_keys')
def available_keys():
    # Contact database to get a list of keys
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute("SELECT * FROM image_key_table1")
    database_key_list = [row[0] for row in cursor.fetchall()]
    return render_template("show_keylist.html",list_title='All Available Keys', input_list=database_key_list, return_addr='/')

@webapp.route('/available_keys',methods=['POST'])
def key_deletion():
    #Clear database
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SET SQL_SAFE_UPDATES = 0;')
    cursor.execute("DELETE FROM image_key_table1")
    cursor.execute('SET SQL_SAFE_UPDATES = 1;')
    db_con.commit()
    #Clear local system
    images = glob.glob('saved_images/*')
    for im in images:
        os.remove(im)

    #Clear Memcache
    memcache_clear_request = requests.post("http://localhost:5001/clear_cache", data={})
    print("Memcache clear: "+memcache_clear_request.text)

    return available_keys()

@webapp.route('/config')
def config():
    return render_template("config.html")

@webapp.route('/config', methods=['POST'])
def process_config():
    print(request.form)
    if 'display' in request.form:
        # TODO: contact mem cache to get the list of keys
        memcache_getkeys_request = requests.get("http://localhost:5001/get_lru_keys")
        print("Memcache Get kes: ")
        print(memcache_getkeys_request.json())
        mecmcache_key_list = memcache_getkeys_request.json()
        return render_template("show_list.html", list_title='All Keys In MemCache', input_list=mecmcache_key_list, return_addr='/config')
    elif 'clear' in request.form:
        #send the clear message to mem cache
        memcache_clear_request = requests.post("http://localhost:5001/clear_cache", data={})
        print("Memcache clear: "+memcache_clear_request.text)
        return render_template("config.html", message = "Cache Cleared!")
    cache_size = request.form.get("cache_size")
    cache_size_float = float(cache_size)
    print(cache_size)

    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('UPDATE cache_config SET capacity =  %s WHERE id = %s',(cache_size,1))
    # the option_selected has 2 possible values (both string): RR and LRU
    option_selected = request.form.get("policyRadios")
    print(option_selected)
    cursor.execute('UPDATE cache_config SET replacement_policy = %s WHERE id = %s',(option_selected,1))
    db_con.commit()
    # TODO: write the options to database and call refreshConfiguration() for memcache

    memcache_refresh_request = requests.post("http://localhost:5001/refresh_configuration")

    print("Memcache refresh: "+memcache_refresh_request.text)

    return render_template("config.html")

@webapp.route('/statistics')
def statistics():
    # TODO: Contact Database to read statistics
    db_con =  get_db()
    cursor= db_con.cursor()
    cursor.execute('SELECT * FROM ( SELECT * FROM cache_stats ORDER BY id DESC LIMIT %s) AS sub ORDER BY id ASC',(121,))
    cache_count=[]
    cache_size=[]
    miss_rate=[]
    hit_rate=[]
    requests_served=[]
    for row in cursor.fetchall():
        cache_count.append(row[2])
        cache_size.append(row[3])
        miss_rate.append(row[4])
        hit_rate.append(row[5])
        requests_served.append(row[6])

  
    x_axis = list(range(0, 605, 5)) 
    cache_count_plot = plot({"data":go.Scatter(x=x_axis, y=cache_count), "layout": go.Layout(title = "Cache Count", xaxis_title = "Time(s)",yaxis_title = "Number of Cache")},output_type='div')
    cache_size_plot = plot({"data":go.Scatter(x=x_axis, y=cache_size), "layout": go.Layout(title = "Cache Size", xaxis_title = "Time(s)",yaxis_title = "MB")},output_type='div')
    miss_rate_plot = plot({"data":go.Scatter(x=x_axis, y=miss_rate), "layout": go.Layout(title = "Miss Rate", xaxis_title = "Time(s)",yaxis_title = "Rate")},output_type='div')
    hit_rate_plot = plot({"data":go.Scatter(x=x_axis, y=hit_rate), "layout": go.Layout(title = "Hit Rate", xaxis_title = "Time(s)",yaxis_title = "Rate")},output_type='div')
    requests_served_plot = plot({"data":go.Scatter(x=x_axis, y=requests_served), "layout": go.Layout(title = "Requests Served", xaxis_title = "Time(s)",yaxis_title = "Number of Request")},output_type='div')
    

    plot_list = [Markup(cache_count_plot),Markup(cache_size_plot),Markup(miss_rate_plot),Markup(hit_rate_plot),Markup(requests_served_plot)]
    return render_template("show_list.html", list_title='MemCache Statistics', input_list=plot_list, return_addr='/')

@webapp.route('/navbar')
def global_navbar():
    return render_template("navbar.html")

@webapp.route('/get',methods=['POST'])
def get():
    key = request.form.get('key')

    if key in memcache:
        value = memcache[key]
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Unknown key"),
            status=400,
            mimetype='application/json'
        )

    return response

@webapp.route('/put',methods=['POST'])
def put():
    key = request.form.get('key')
    value = request.form.get('value')
    memcache[key] = value

    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )

    return response

