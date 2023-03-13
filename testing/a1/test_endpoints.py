import argparse
import json
import requests

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5000
DEFAULT_IMAGE_PATH = 'test_images/dog.jpg'

DELETE_REL_URL = '/api/delete_all'
UPLOAD_REL_URL = '/api/upload'
LIST_KEYS_REL_URL = '/api/list_keys'
RETRIEVE_REL_URL = '/api/key'


def delete_all(base_url):
    expected_response = {'success': 'true'}
    response = requests.post(f'{base_url}{DELETE_REL_URL}')
    response_json = response.json()

    print(f'DELETE: {json.dumps(response_json, indent=4)}')
    assert response_json == expected_response


def upload(base_url, key, image_path):
    expected_response = {'success': 'true', 'key': key}

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    response = requests.post(f'{base_url}{UPLOAD_REL_URL}', data={'key': key}, files={'file': image_bytes})
    response_json = response.json()

    print(f'UPLOAD: {json.dumps(response_json, indent=4)}')
    assert response_json == expected_response


def list_keys(base_url):
    response = requests.post(f'{base_url}{LIST_KEYS_REL_URL}')
    response_json = response.json()

    print(f'LIST_KEYS: {json.dumps(response_json, indent=4)}')
    assert response_json['success'] == 'true'


def get_image(base_url, key):
    response = requests.post(f'{base_url}{RETRIEVE_REL_URL}/{key}')
    response_json = response.json()

    print(f'GET_IMAGE: {json.dumps(response_json, indent=4)}')
    assert response_json['success'] == 'true'


def test_all(base_url, image_path):
    delete_all(base_url)
    upload(base_url, 'test_key', image_path)
    list_keys(base_url)
    get_image(base_url, 'test_key')
    delete_all(base_url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default=DEFAULT_HOST, help='')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='')
    parser.add_argument('--image_path', type=str, default=DEFAULT_IMAGE_PATH)
    args = parser.parse_args()

    base_url = f'http://{args.host}:{args.port}'

    test_all(base_url, args.image_path)
