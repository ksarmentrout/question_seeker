import os
from dotenv import load_dotenv

load_dotenv()


def myenv(value):
    return os.environ.get(value)


class Config(object):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{myenv("MYSQL_USER")}:{myenv("MYSQL_PASS")}@{myenv("MYSQL_HOST")}/{myenv("MYSQL_DB")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
