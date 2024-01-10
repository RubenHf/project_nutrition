# run pytest in the folder to test

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"health_check": "OK"}

def test_process_urls_endpoint():

    test_data = {"data_file_S3": 'files/cleaned_data_test.csv', "data_file_S3_post_clean_up": 'files/cleaned_image_data_test.csv'}

    response = client.post("/process-data-urls/", data=test_data)
    
    assert response.status_code == 200

def test_process_image_endpoint():

    test_data = {"data_file_S3": 'files/cleaned_image_data_test.csv', "data_file_S3_post_clean_up": 'files/cleaned_image_data_test_end.csv'}
    
    response = client.post("/process-data-image/", data=test_data)

    assert response.status_code == 200