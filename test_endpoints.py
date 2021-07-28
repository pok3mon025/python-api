import pytest
import bcrypt
import config
import json

from sqlalchemy import create_engine, text
from app import create_app

database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)


@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TESTING'] = True
    api = app.test_client()

    return api


def setup_function():
    # Create a test user
    hashed_password = bcrypt.hashpw(
        b"test password",
        bcrypt.gensalt()
    )
    new_users = [
        {
            'id': 1,
            'name': '송은우',
            'email': 'songew@gamil.com',
            'profile': 'test profile',
            'hashed_password': hashed_password
        }, {
            'id': 2,
            'name': '김철수',
            'email': 'test@gamil.com',
            'profile': 'test profile',
            'hashed_password': hashed_password
        }
    ]
    database.execute(text("""
        INSERT INTO users (
            id,
            name,
            email,
            profile,
            hashed_password
        ) VALUES (
            :id,
            :name,
            :email,
            :profile,
            :hashed_password
        )
    """), new_users)

    # User 2의 트윗 미리 생성해 놓기
    database.execute(text("""
        INSERT INTO tweets (
            user_id,
            tweet
        ) VALUES (
            2,
            "Hello World!"
        )
    """))


def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))


def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data


def test_login(api):
    resp = api.post(
        '/login',
        data=json.dumps({
            'email': 'songew@gamil.com',
            'password': 'test password'
        }),
        content_type='application/json'
    )
    assert b"access_token" in resp.data


def test_unauthorized(api):
    # access token이 없이는 401 응답을 리턴하는지를 확인
    resp = api.post(
        '/tweet',
        data=json.dumps({
            'tweet': "Hello World!"
        }),
        content_type='application/json'
    )
    assert resp.status_code == 401

    resp = api.post(
        '/unfollow',
        data=json.dumps({
            'unfollow': 2
        }),
        content_type='application/json'
    )
    assert resp.status_code == 401


def test_tweet(api):
    # Login
    resp = api.post(
        '/login',
        data=json.dumps({
            'email': 'songew@gmail.com',
            'password': 'test password'
        }),
        content_type='application/json'
    )
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    # tweet
    resp = api.post(
        '/tweet',
        data=json.dumps({
            'tweet': "Hello World!"
        }),
        content_type='application/json',
        headers={'Authorization': access_token}
    )
    assert resp.status_code == 200

    # Check tweet
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': 1,
        'timeline': [
            {
                'user_id': 1,
                'tweet': "Hello World!"
            }
        ]
    }
