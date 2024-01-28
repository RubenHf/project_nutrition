from fastapi.testclient import TestClient
import requests
import base64
import sys
import os

# Get the current working directory 
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Importing main
from main import app

client = TestClient(app)

def test_front_process_image():

    # Two links to try out
    url_failed = "https://images.openfoodfacts.org/images/products/1281/1.400.jpg"
    
    url_succeeded = "https://images.openfoodfacts.org/images/products/1885/1.400.jpg"
    
    content_failed = requests.get(url_failed).content
    content_succeeded = requests.get(url_succeeded).content
    
    files_failed = {"file": ('temp_image.jpg', content_failed, 'image/jpg')}
    files_succeeded = {"file": ('temp_image.jpg', content_succeeded, 'image/jpg')}
    
    response_failed = client.post("/front-process-image/", files = files_failed)
    response_succeeded = client.post("/front-process-image/", files = files_succeeded)

    assert response_failed.status_code == 200
    assert response_succeeded.status_code == 200

    assert response_failed.json() == "None"
    assert response_succeeded.json()['result'] in ['0', '1']

def test_pnns_process_image_files():

    # Two links to try out
    url_failed = "https://images.openfoodfacts.org/images/products/1281/1.400.jpg"
    
    url_succeeded = "https://images.openfoodfacts.org/images/products/1885/1.400.jpg"
    
    content_failed = requests.get(url_failed).content
    content_succeeded = requests.get(url_succeeded).content
    
    files_failed = {"file": ('temp_image.jpg', content_failed, 'image/jpg')}
    files_succeeded = {"file": ('temp_image.jpg', content_succeeded, 'image/jpg')}
    
    response_failed = client.post("/pnns-process-image/", files = files_failed)
    response_succeeded = client.post("/pnns-process-image/", files = files_succeeded)

    assert response_failed.status_code == 200
    assert response_succeeded.status_code == 200

    assert response_failed.json()['status'] == 'error'
    assert 'cannot identify image file' in response_failed.json()['message']

    assert isinstance(response_succeeded.json(), list)
    assert 'pnns_groups' in response_succeeded.json()[0]

def test_pnns_process_image_b64():

    # Two links to try out
    url_failed = "https://images.openfoodfacts.org/images/products/1281/1.400.jpg"
    url_succeeded = "https://images.openfoodfacts.org/images/products/1885/1.400.jpg"
    
    content_failed = requests.get(url_failed).content
    content_succeeded = requests.get(url_succeeded).content

    b64_image_failed = base64.b64encode(content_failed).decode('utf-8')
    image_contents_failed = {"base64_image": b64_image_failed, "pnns_groups": "pnns_groups_1"}

    b64_image_succeeded = base64.b64encode(content_succeeded).decode('utf-8')
    image_contents_succeeded = {"base64_image": b64_image_succeeded, "pnns_groups": "pnns_groups_1"}
    
    response_failed = client.post("/pnns-process-image/", data = image_contents_failed)
    response_succeeded = client.post("/pnns-process-image/", data = image_contents_succeeded)

    assert response_failed.status_code == 200
    assert response_succeeded.status_code == 200

    assert response_failed.json()['status'] == 'error'
    assert 'cannot identify image file' in response_failed.json()['message']

    assert isinstance(response_succeeded.json(), list)
    assert 'pnns_groups' in response_succeeded.json()[0]
