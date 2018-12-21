import json
import time
from typing import List, Union

import backoff
import fire
from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener

from question_seeker import q_starts
from question_seeker import utils
from question_seeker.utils import logger


class Listener(StreamListener):
    def __init__(self, tracking: List[str], time_limit: Union[None, int]=None, output_filename: str='tweets.json', batch_size: int=20, write_to_file: bool=True):
        super().__init__()
        self.tracking = tracking
        self.time_limit = time_limit
        self.file = open(output_filename, 'a')
        self.batch_size = batch_size
        self.write_to_file = write_to_file

        self.start_time = time.time()
        self.tweet_list = []

    def process_tweets(self):
        """Filters a batch of collected tweets for the presence of one of the tracked questions, then writes to file.
        Resets the retained tweet list to start a new batch.
        """
        parsed_tweets = utils.parse_tweets(self.tweet_list, self.tracking)
        if self.write_to_file:
            if parsed_tweets:
                self.file.writelines(parsed_tweets)
                logger.debug(f'Wrote {len(parsed_tweets)} tweets to file')
        self.tweet_list = []

    def on_data(self, data: str) -> bool:
        """Processes incoming tweet data from Twitter API stream.

        Args:
            data: string representation of a dictionary with tweet and metadata

        Returns:
            True to continue streaming, False to stop streaming if the time limit elapses.
        """
        def process_tweet(t_data):
            self.tweet_list.append(json.loads(t_data))
            if len(self.tweet_list) >= self.batch_size:
                self.process_tweets()
            return True

        if self.time_limit:
            # Check if the time limit has elapsed
            if time.time() - self.start_time < self.time_limit:
                process_tweet(data)
            else:
                self.file.close()
                print('Stopping tweet collection')
                logger.info('Stopping tweet collection')
                return False
        else:
            # Process data infinitely
            process_tweet(data)

    def on_error(self, status):
        """If there is some Twitter API error, sends a notification and raises a ConnectionError.

        Args:
            status: API error code
        """
        self.file.close()
        logger.error(f'Twitter API connection failed with status code {status}. Reconnecting.')
        utils.send_sms(f'Twitter API connection failed with status code {status}. Reconnecting.')
        raise ConnectionError(status)


@backoff.on_exception(backoff.expo, ConnectionError, max_tries=8,
                      on_giveup=lambda x: utils.send_sms('Giving up reconnecting after 8 tries. App down.'))
def connect_stream(
        auth: OAuthHandler, tracking: List[str], time_limit: Union[int, None], output_filename: str='tweets.json',
        batch_size: int=20, write_to_file: bool=True
):
    """

    Args:
        auth: authenticated Twitter API object
        tracking: list, question starts from q_starts.py to track
        time_limit: int or None, amount of time to keep the stream open. Setting to None listens indefinitely
        output_filename: str, name of a file to write to
        batch_size: int, number of tweets to hold in memory before parsing. In v1 without multiprocessing, this is set
            low by default so that the parsing and writing doesn't block getting additional stream data.
        write_to_file: bool, whether to write tweets to a file. Can set False for testing purposes.
    """
    # Create a new listener and stream
    logger.info('Creating Listener and Stream')
    agent = Listener(tracking, time_limit, output_filename, batch_size=batch_size, write_to_file=write_to_file)
    t_stream = Stream(auth, agent)

    # Begin streaming
    logger.info('Beginning streaming')
    t_stream.filter(track=tracking)


def stream(
        q_list_name: str, time_limit: Union[int, None]=None, output_filename: str='tweets.json', batch_size: int=20,
        write_to_file: bool=True
):
    """

    Args:
        q_list_name: str, key to fetch the question list from q_starts.py
        time_limit: int or None, amount of time to keep the stream open. Setting to None listens indefinitely
        output_filename: str, name of a file to write to
        batch_size: int, number of tweets to hold in memory before parsing. In v1 without multiprocessing, this is set
            low by default so that the parsing and writing doesn't block getting additional stream data.
        write_to_file: bool, whether to write tweets to a file. Can set False for testing purposes.

    Returns:
        True if all goes well and the function ends normally
    """
    auth = utils.get_auth()

    # Select which question list to track
    tracking = q_starts.get_q_list(q_list_name)

    # Connect to a stream using exponential backoff in the event of a connection error
    connect_stream(auth, tracking, time_limit, output_filename, batch_size=batch_size, write_to_file=write_to_file)

    return True


if __name__ == '__main__':
    fire.Fire(stream)
