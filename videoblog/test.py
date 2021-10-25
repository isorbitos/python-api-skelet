# pytest test.py
from . import client

def test_simple():
    my_list = [1, 2, 3, 4]
    assert 3 in my_list

def test_get():
    res = client.get('/tutorials')
    assert res.status_code == 200

def test_post():
    data={
            'id': 3,
            'title': 'Video nr4 cool video',
            'description': 'test, put post'
    }

    res = client.post('/tutorials', json=data)
    assert res.status_code ==200
    assert res.get_json()[-1]['title'] == 'Video nr4 cool video'