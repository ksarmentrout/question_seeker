import os

from question_seeker import (
    q_starts,
    processing,
)


class TestProcessing:
    @classmethod
    def setup_class(cls):
        # Use ['why am', 'y am'] to check
        cls.tracking_list, cls.filename = q_starts.get_q_list_and_filename('personal')
        cls.pass1 = {'text': 'Why am I so tired?'}
        cls.pass2 = {'text': "It's late, why am I still building this?"}
        cls.pass3 = {'text': '...so y am I here?'}
        cls.pass4 = {'text': "Why can't they just fly the eagles to Mordor?"}
        cls.pass5 = {'text': "I'M YELLING\nWHY AM I YELLING?"}
        cls.fail1 = {'text': 'Can someone tell me what to do?'}
        cls.fail2 = {'text': "how does anyone not like pizza?"}
        cls.fail3 = {'text': "why am I ignoring proper punctuation"}
        cls.track_list_ids = ['personal', 'capacity']
        cls.tweet_list = [
            cls.pass1, cls.pass2, cls.pass3, cls.pass4, cls.pass5, cls.fail1, cls.fail2, cls.fail3
        ]
        cls.batch_size = 10

    @classmethod
    def teardown_class(cls):
        """
        Remove all generated files
        """
        for filename in [
            'all_tweets.json',
            'capacity_tweets.json',
            'personal_tweets.json',
        ]:
            os.remove(filename)

    def test_tweet_handler_map(self):
        tweet_handler_map = processing.get_tweet_handler_map(self.track_list_ids, self.batch_size, write_to_file=False)
        assert set(tweet_handler_map.keys()) == set(q_starts.personal_starts + q_starts.capacity_starts)

    def test_get_full_tracking_list(self):
        tweet_handler_map = processing.get_tweet_handler_map(self.track_list_ids, self.batch_size, write_to_file=False)
        full_list = processing.get_full_tracking_list(tweet_handler_map)
        assert sorted(full_list) == sorted(q_starts.personal_starts + q_starts.capacity_starts)

    def test_process_tweets(self):
        tweet_handler_map = processing.get_tweet_handler_map(self.track_list_ids, self.batch_size, write_to_file=False)
        processing.process_tweets(self.tweet_list, tweet_handler_map)
        assert len(tweet_handler_map['why am'].bucket) == 4
        assert len(tweet_handler_map['why can'].bucket) == 1

