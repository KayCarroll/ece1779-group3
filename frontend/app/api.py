import base64
import glob
import json
import os
import requests

from flask import request
from io import BytesIO
from PIL import Image

from app import webapp
from app.main import get_db

CACHE_API_BASE_URL = 'http://localhost:5001'
IMAGE_DIR = 'saved_images'
TABLE_NAME = 'image_key_table1'


@webapp.route('/api/delete_all', methods=['POST'])
def delete_all():
    try:
        cache_response = requests.post(f'{CACHE_API_BASE_URL}/clear_cache')

        db_con =  get_db()
        cursor = db_con.cursor()
        cursor.execute('SET SQL_SAFE_UPDATES = 0;')
        cursor.execute(f'DELETE FROM {TABLE_NAME}')
        cursor.execute('SET SQL_SAFE_UPDATES = 1;')
        db_con.commit()

        for image_path in glob.glob(f'{IMAGE_DIR}/*'):
            os.remove(image_path)

        response = webapp.response_class(response=json.dumps({'success': 'true'}), status=200)
    except Exception as e:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'error': {'code': 400, 'message': str(e)}}), status=400)
    return response


@webapp.route('/api/upload', methods=['POST'])
def upload():
    try:
        key = request.form.get('key')
        image_file = request.files['file']
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)
        image_file.save(f'{IMAGE_DIR}/{key}')

        db_con =  get_db()
        cursor = db_con.cursor()
        cursor.execute(f'SELECT image_key FROM {TABLE_NAME} WHERE BINARY image_key = BINARY %s GROUP BY image_key', (key,))
        exist = cursor.fetchone()
        if exist is None:
            cursor.execute(f'INSERT INTO {TABLE_NAME} VALUES(%s)', (key,))
            db_con.commit()

        cache_response = requests.post(f'{CACHE_API_BASE_URL}/invalidate_key', data={'key': key})

        response = webapp.response_class(response=json.dumps({'success': 'true',
                                                              'key': key}), status=200)
    except Exception as e:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'error': {'code': 400, 'message': str(e)}}), status=400)
    return response


@webapp.route('/api/list_keys', methods=['POST'])
def list_keys():
    try:
        db_con =  get_db()
        cursor= db_con.cursor()
        cursor.execute(f'SELECT * FROM {TABLE_NAME}')
        database_key_list = [row[0] for row in cursor.fetchall()]

        response = webapp.response_class(response=json.dumps({'success': 'true',
                                                              'keys': database_key_list}), status=200)
    except Exception as e:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'error': {'code': 400, 'message': str(e)}}), status=400)
    return response


@webapp.route('/api/key/<key_value>', methods=['POST'])
def get_image(key_value):
    try:
        cache_response = requests.get(f'{CACHE_API_BASE_URL}/get_image/{key_value}')
        if cache_response.status_code == 200:
            image_str = cache_response.json()
        else:
            image = Image.open(f'{IMAGE_DIR}/{key_value}')
            buffer = BytesIO()
            image.save(buffer, format=image.format)
            image_str = base64.b64encode(buffer.getvalue())

        cache_response = requests.post(f'{CACHE_API_BASE_URL}/cache_image',
                                       data={'key': key_value ,'value': image_str.decode('utf-8')})

        response = webapp.response_class(response=json.dumps({'success': 'true', 'key': key_value,
                                                              'content': image_str.decode('utf-8')}), status=200)
    except Exception as e:
        response = webapp.response_class(response=json.dumps({'success': 'false',
                                                              'error': {'code': 400, 'message': str(e)}}), status=400)
    return response
