db = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': 3306,
    'database': 'miniter'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
JWT_SECRET_KEY = 'miniter'

test_db = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': 3306,
    'database': 'minister_test'
}

test_config = {
    'DB_URL': f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
    'JWT_SECRET_KEY': 'miniter',
    'JWT_EXP_DELTA_SECONDS': 7 * 24 * 60 * 60
}
