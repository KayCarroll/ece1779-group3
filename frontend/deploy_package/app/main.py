
from flask import render_template, url_for, request
from app import webapp, memcache
from flask import json
from PIL import Image
from pathlib import Path
import io
import base64
import os


@webapp.route('/')
def main():
    return render_template("main.html")

@webapp.route('/upload_image')
def render_upload_image():
    return render_template("upload.html")

@webapp.route('/upload_image', methods=['POST'])
def upload_image():
    file_name = request.form.get("text")
    # TODO: Check the key is not duplicate, if it is, replace the old file
    # TODO: add the key to the list of known keys in the database
    file = request.files['my_image']
    file_path = "saved_images/" + file_name + ".jpg"
    isExist = os.path.exists("saved_images")
    if not isExist:
        os.makedirs("saved_images")
        print("Saved images directory is created!")
    file.save(file_path)
    return render_template('message.html', user_message = "Your image has been uploaded successfully", return_addr='/upload_image')

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
    # TODO: check if key exist in database
    # TODO: check if key exist in mem cache
    # Placeholder: reading directly from file system all the time
    img_file_path = "saved_images/" + file_name + ".jpg"
    path = Path(img_file_path)
    if not path.is_file():
        return render_template('message.html', user_message = "The key you specified does not exist in the database", return_addr='/show_image')
    print (img_file_path)
    im = Image.open(img_file_path)
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return render_template('show_image.html', img_data = encoded_img_data.decode('utf-8'))

@webapp.route('/available_keys')
def available_keys():
    # TODO: Contact database to get a list of keys
    placeholder_list = ['item1', 'item2', 'item3']
    return render_template("show_list.html", list_title='All Available Keys (PLACEHOLDER ONLY)', input_list=placeholder_list, return_addr='/')

@webapp.route('/config')
def config():
    return render_template("config.html")

@webapp.route('/config', methods=['POST'])
def process_config():
    print(request.form)
    if 'display' in request.form:
        # TODO: contact mem cache to get the list of keys
        placeholder_list = ['item1', 'item2', 'item3']
        return render_template("show_list.html", list_title='All Keys In MemCache (PLACEHOLDER ONLY)', input_list=placeholder_list, return_addr='/config')
    elif 'clear' in request.form:
        # TODO: send the clear message to mem cache
        return render_template("config.html", message = "Cache Cleared!")
    cache_size = request.form.get("cache_size")
    cache_size_float = float(cache_size)
    print(cache_size)
    # the option_selected has 2 possible values (both string): RR and LRU
    option_selected = request.form.get("policyRadios")
    print(option_selected)
    # TODO: write the options to database and call refreshConfiguration() for memcache
    return render_template("config.html")

@webapp.route('/statistics')
def statistics():
    # TODO: Contact Database to read statistics
    placeholder_list = ["Number of Items in Cache: 43", "Cache Size Used: 102.5MB", "Number of Request Served: 72", "Hit Rate: 50%", "Miss Rate: 50%"]
    return render_template("show_list.html", list_title='MemCache Statistics (PLACEHOLDER ONLY)', input_list=placeholder_list, return_addr='/')

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

