import unittest

import tweepy

from question_seeker import multifile_stream as streamer
from question_seeker import utils, q_starts


class TestStreamer(unittest.TestCase):
    def setUp(self):
        # Use ['why am', 'y am'] to check
        self.tracking_list, self.filename = q_starts.get_q_list_and_filename('personal')
        self.pass1 = {'text': 'Why am I so tired?'}
        self.pass2 = {'text': "It's late, why am I still building this?"}
        self.pass3 = {'text': '...so y am I here?'}
        self.pass4 = {'text': "Why can't they just fly the eagles to Mordor?"}
        self.pass5 = {'text': "I'M YELLING\nWHY AM I YELLING?"}
        self.fail1 = {'text': 'Can someone tell me what to do?'}
        self.fail2 = {'text': "how does anyone not like pizza?"}
        self.fail3 = {'text': "why am I ignoring proper punctuation"}
        self.track_list_ids = ['personal', 'capacity']
        self.tweet_list = [
            self.pass1, self.pass2, self.pass3, self.pass4, self.pass5, self.fail1, self.fail2, self.fail3
        ]
        self.batch_size = 10

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
        assert sorted(full_list) == sorted(q_starts.personal_starts + q_starts.capacity_starts)

    def test_process_tweets(self):
        tweet_handler_map = utils.get_tweet_handler_map(self.track_list_ids, self.batch_size, write_to_file=False)
        utils.process_tweets(self.tweet_list, tweet_handler_map)
        assert len(tweet_handler_map['why am'].bucket) == 4
        assert len(tweet_handler_map['why can'].bucket) == 1

    def test_send_sms(self):
        status = utils.send_sms('Keep up the good work! :)')
        assert status == 200
