import bcrypt
import pytest
import config

from model import UserDao, TweetDao
from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)


@pytest.fixture
def user_dao():
    return UserDao(database)


@pytest.fixture()
def tweet_dao():
    return TweetDao(database)


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
            'email': 'songew@gmail.com',
            'profile': 'test profile',
            'hashed_password': hashed_password
        }, {
            'id': 2,
            'name': '김철수',
            'email': 'test@gmail.com',
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


def get_user(user_id):
    row = database.execute(text("""
        SELECT
            id,
            name,
            email,
            profile
        FROM users
        WHERE id = :user_id
    """), {
        'user_id': user_id
    }).fetchone()

    return {
        'id': row['id'],
        'name': row['name'],
        'email': row['email'],
        'profile': row['profile']
    } if row else None


def get_follow_list(user_id):
    rows = database.execute(text("""
        SELECT follow_user_id as id
        FROM users_follow_list
        WHERE user_id = :user_id
    """), {
        'user_id': user_id
    }).fetchall()

    return [int(row['id']) for row in rows]


def test_insert_user(user_dao):
    new_user = {
        'name': '홍길동',
        'email': 'hong@test.com',
        'profile': '서쪽에서 번쩍, 동쪽에서 번쩍',
        'password': 'test1234'
    }

    new_user_id = user_dao.insert_user(new_user)
    user = get_user(new_user_id)

    assert user == {
        'id': new_user_id,
        'name': new_user['name'],
        'email': new_user['email'],
        'profile': new_user['profile']
    }


def test_get_user_id_and_password(user_dao):
    # get_user_id_and_password 메소드를 호출하여 사용자의 아이디와 비밀번호 해시 값을 읽어 들인다.
    # 사용자는 이미 setup_function에서 생성된 사용자를 사용한다.
    user_credential = user_dao.get_user_id_and_password(email='songew@gmail.com')

    # 먼저 사용자 아이디가 맞는지 확인한다.
    assert user_credential['id'] == 1

    # 그리고 사용자 비밀버호가 맞는지 bcrypt의 checkpw 메소드를 사용해서 확인한다.
    assert bcrypt.checkpw('test password'.encode('UTF-8'),
                          user_credential['hashed_password'].encode('UTF-8'))


def test_insert_unfollow(user_dao):
    # insert_follow 메소드를 사용하여 사용자 1이 사용자 2를 팔로우한 후 언팔로우한다.
    # 사용자 1과 2는 setup_function에서 이미 생성되었다.
    user_dao.insert_follow(user_id=1, follow_id=2)
    user_dao.insert_unfollow(user_id=1, unfollow_id=2)

    follow_list = get_follow_list(1)

    assert follow_list == []


def test_insert_tweet(tweet_dao):
    tweet_dao.insert_tweet(1, "tweet test")
    timeline = tweet_dao.get_timeline(1)

    assert timeline == [
        {
            'user_id': 1,
            'tweet': 'tweet test'
        }
    ]


def test_timeline(user_dao, tweet_dao):
    tweet_dao.insert_tweet(1, "tweet test")
    tweet_dao.insert_tweet(2, "tweet test2")
    user_dao.insert_follow(1, 2)

    timeline = tweet_dao.get_timeline(1)

    assert timeline == [
        {
            'user_id': 2,
            'tweet': 'Hello World!'
        },
        {
            'user_id': 1,
            'tweet': 'tweet test'
        },
        {
            'user_id': 2,
            'tweet': 'tweet test2'
        }
    ]
