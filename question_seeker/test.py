import unittest

import tweepy

from question_seeker import multifile_stream as streamer
from question_seeker import utils, q_starts


class TestStreamer(unittest.TestCase):
    def setUp(self):
        # Use ['why am', 'y am'] to check
        self.tracking_list, self.filename = q_starts.get_q_list_and_filename('personal')
        self.tweet_pass1 = {'text': 'Why am I so tired?', 'retweeted': False}
        self.tweet_pass2 = {'text': "It's late, why am I still building this?", 'retweeted': False}
        self.tweet_pass3 = {'text': '...so y am I here?', 'retweeted': False}
        self.tweet_fail1 = {'text': "Why can't they just fly the eagles to Mordor?", 'retweeted': False}
        self.tweet_fail2 = {'text': "how does anyone not like pizza?", 'retweeted': False}
        self.tweet_fail3 = {'text': "why am I ignoring proper punctuation", 'retweeted': False}
        self.track_list_ids = ['personal', 'capacity']
        self.tweet_list = [self.tweet_pass1, self.tweet_fail1]
        self.batch_size = 2

    def test_aws_creds(self):
        # Loads credentials and validates against AWS validation endpoint
        auth = utils.get_auth()
        api = tweepy.API(auth)

        # This function returns a User object if the credentials are valid, False otherwise
        assert type(api.verify_credentials()) == tweepy.User

    def test_stream(self):
        stream_result = streamer.stream('all', time_limit=1, write_to_file=False)
        assert stream_result is True

    def test_tweet_handler_map(self):
        tweet_handler_map = utils.get_tweet_handler_map(self.track_list_ids, self.batch_size, write_to_file=False)
        assert set(tweet_handler_map.keys()) == set(q_starts.personal_starts + q_starts.capacity_starts)

    def test_get_full_tracking_list(self):
        tweet_handler_map = utils.get_tweet_handler_map(self.track_list_ids, self.batch_size, write_to_file=False)
        full_list = utils.get_full_tracking_list(tweet_handler_map)
        assert full_list == q_starts.personal_starts + q_starts.capacity_starts

    def test_process_tweets(self):
        tweet_handler_map = utils.get_tweet_handler_map(self.track_list_ids, self.batch_size, write_to_file=False)
        utils.process_tweets(self.tweet_list, tweet_handler_map)
        print(tweet_handler_map)
        assert len(tweet_handler_map['why am'].bucket) == 1
        assert len(tweet_handler_map['why can'].bucket) == 0

    def test_send_sms(self):
        status = utils.send_sms('Keep up the good work! :)')
        assert status == 200
