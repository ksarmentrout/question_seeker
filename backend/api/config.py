import os
from dotenv import load_dotenv

load_dotenv()


def myenv(value):
    return os.environ.get(value)


class Config(object):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{myenv("MYSQL_DB_USER")}:{myenv("MYSQL_DB_PASS")}'
        f'@{myenv("MYSQL_DB_HOST")}/{myenv("MYSQL_DB_NAME")}?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MYSQL_DATABASE_CHARSET = 'utf8mb4'

