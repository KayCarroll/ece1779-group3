
from flask import render_template, url_for, request
from app import webapp, memcache
from flask import json


@webapp.route('/')
def main():
    return render_template("main.html")

@webapp.route('/upload_image')
def render_upload_image():
    return render_template("upload.html")

@webapp.route('/upload_image', methods=['POST'])
def upload_image():
    file_name = request.form.get("text")
    print("received file name: " + file_name)
    # TODO: Check the key is not duplicate, if it is, replace the old file
    # TODO: add the key to the list of known keys in the database
    print(request.files)
    file = request.files['my_image']
    file.save("saved_images/" + file_name + ".jpg")
    print(file)
    return 'File uploaded successfully'

@webapp.route('/show_image')
def render_show_image():
    img_file_path = 'saved_images/dsfsdaf.jpg'
    return render_template('show_image.html', user_image = img_file_path)

@webapp.route('/show_image', methods=['POST'])
def show_image():
    img_file_path = 'saved_images/dsfsdaf.jpg'
    return render_template('show_image.html', user_image = img_file_path)

@webapp.route('/available_keys')
def available_keys():
    return render_template("main.html")

@webapp.route('/config')
def config():
    return render_template("main.html")

@webapp.route('/statistics')
def statistics():
    return render_template("main.html")

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

