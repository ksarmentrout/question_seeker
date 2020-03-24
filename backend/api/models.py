import datetime
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta


db = SQLAlchemy()


class Tweet(db.Model):
    __tablename__ = 'tweet'
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow(), nullable=False)
    tweet_text = db.Column(db.String(280), nullable=False)
    tweet_id = db.Column(db.String(32), nullable=False, unique=True)
    tweet_timestamp = db.Column(db.String(64), nullable=False)
    loc_name = db.Column(db.String(128), nullable=True)
    country = db.Column(db.String(128), nullable=True)
    permalink_slug = db.Column(db.String(7), nullable=True)

    def __repr__(self):
        return '<Tweet: %r>' % self.tweet_text


def to_dict(obj):
    if isinstance(obj.__class__, DeclarativeMeta):
        # an SQLAlchemy class
        fields = {}
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
            data = obj.__getattribute__(field)
            try:
                json.dumps(data)  # this will fail on non-encodable values, like other classes
                if data is not None:
                    fields[field] = data
            except TypeError:
                pass
        # a json-encodable dict
        return fields
