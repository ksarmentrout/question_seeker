import json
import unittest

import tweepy

from question_seeker import tweepy_stream as streamer
from question_seeker import utils, q_starts


class TestStreamer(unittest.TestCase):
    def setUp(self):
        # Use ['why am', 'y am'] to check
        self.tracking_list = q_starts.get_q_list('personal')
        self.pass1 = 'Why am I so tired?'
        self.pass2 = "It's late, why am I still building this?"
        self.pass3 = '...so y am I here?'
        self.fail1 = "Why can't they just fly the eagles to Mordor?"
        self.fail2 = "how does anyone not like pizza?"
        self.fail3 = "why am I ignoring proper punctuation"

    def test_aws_creds(self):
        # Loads credentials and validates against AWS validation endpoint
        auth = utils.get_auth()
        api = tweepy.API(auth)

        # This function returns a User object if the credentials are valid, False otherwise
        assert type(api.verify_credentials()) == tweepy.User

    def test_stream(self):
        stream_result = streamer.stream('all', time_limit=1, write_to_file=False)
        assert stream_result is True

    def test_parser(self):
        assert utils.parse(self.pass1, self.tracking_list) is True
        assert utils.parse(self.pass2, self.tracking_list) is True
        assert utils.parse(self.pass3, self.tracking_list) is True
        assert utils.parse(self.fail1, self.tracking_list) is None
        assert utils.parse(self.fail2, self.tracking_list) is None
        assert utils.parse(self.fail3, self.tracking_list) is None

    def test_batch_parser(self):
        tweet_list = [self.pass1, self.pass2, self.fail1, self.fail2]
        tweet_dict_list = [{'text': x} for x in tweet_list]
        passing_dict_list = [json.dumps({'text': x}) for x in [self.pass1, self.pass2]]
        surviving_tweets = utils.parse_tweets(tweet_dict_list, self.tracking_list)
        assert surviving_tweets == passing_dict_list

    def test_send_sms(self):
        status = utils.send_sms('Keep up the good work! :)')
        assert status == 200
