import json

def test_check_GET(client):
    response = client.get('/check')
    json_data = json.loads(response.data)
    assert json_data['health'] == 'ok'
