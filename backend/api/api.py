from flask import jsonify
from flask_restful import (
    Api,
    Resource,
)
from sqlalchemy.sql.expression import func

from .models import (
    to_dict,
    Tweet as TweetModel,
)


api = Api()


class Tweet(Resource):
    '''
    Fetches all tweets.
    '''
    def get(self):
        return jsonify([to_dict(tweet) for tweet in TweetModel.query.all()])


class RandomTweets(Resource):
    def get(self):
        '''
        The performance of this method will degrade once db becomes large because it
        requires a full db scan. May need to change how it's done.
        Another method would be to add a random number column to the db and sort by
        some offset of that column.
        '''
        tweets = TweetModel.query.order_by(func.random()).limit(200).all()
        return jsonify([to_dict(tweet) for tweet in tweets])


class PermalinkTweet(Resource):
    '''
    Fetches on the tweet that has a permalink slug matching the URL input.
    '''
    def get(self, permalink_slug):
        tweets = TweetModel.query.filter_by(permalink_slug=permalink_slug).all()
        return jsonify([to_dict(tweet) for tweet in tweets])


# class OptimizedRandomTweets(Resource):
#     def get(self):
#         tweets = TweetModel.query.options(load_only('id')).offset(
#             func.floor(
#                 func.random() *
#                 db.session.query(func.count(TweetModel.id))
#             )
#         ).limit(1).all()
#         return jsonify([to_dict(tweet) for tweet in tweets])


# api.add_resource(Tweet, '/')
api.add_resource(RandomTweets, '/random')
api.add_resource(PermalinkTweet, '/tweet/<string:permalink_slug>')
# api.add_resource(OptimizedRandomTweets, '/optimized_random')
