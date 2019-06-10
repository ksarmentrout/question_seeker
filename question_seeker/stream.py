import datetime
import json
import time
from typing import (
    Dict,
    List,
    Optional,
    Union,
)

import backoff
import fire
from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener

from question_seeker import log, utils


logger = log.LOGGER


class Listener(StreamListener):
    def __init__(
            self,
            tweet_handler_map: Dict[str, utils.TweetHandler],
            time_limit: Optional[int] = None,
            batch_size: int = 50,
            write_to_file: bool = True,
    ):
        super().__init__()
        self.tweet_handler_map = tweet_handler_map
        self.time_limit = time_limit
        self.batch_size = batch_size
        self.write_to_file = write_to_file

        self.start_time = time.time()
        self.tweet_list = []
        self.total_tweet_counter = 0
        self.tweet_count_file = utils.FileWrapper('tweet_counter.txt')

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
                utils.process_tweets(self.tweet_list, self.tweet_handler_map)
                self.total_tweet_counter += len(self.tweet_list)
                if self.total_tweet_counter % 1000 == 0:
                    self.report_tweet_count()
                self.tweet_list = []
            return True

        if self.time_limit:
            # Check if the time limit has elapsed
            if time.time() - self.start_time < self.time_limit:
                process_tweet(data)
            else:
                print('Stopping tweet collection')
                logger.info('Stopping tweet collection')
                utils.process_tweets(self.tweet_list, self.tweet_handler_map, force_write=True)
                return False
        else:
            # Process data infinitely
            process_tweet(data)

    def report_tweet_count(self):
        # Report number of tweets collected
        report_line = f'{self.total_tweet_counter},{datetime.datetime.now()}'
        self.tweet_count_file.write(report_line)

    def on_error(self, status: int):
        """If there is some Twitter API error, sends a notification and raises a ConnectionError.

        Args:
            status: API error code
        """
        # Write all held tweets to files before closing
        self.total_tweet_counter += len(self.tweet_list)
        utils.process_tweets(self.tweet_list, self.tweet_handler_map, force_write=True)

        # Close files
        for tweet_handler in self.tweet_handler_map.values():
            tweet_handler.file.close()

        # Report number of tweets
        self.report_tweet_count()
        self.tweet_count_file.close()

        # Raise error
        logger.error(f'Twitter API connection failed with status code {status}. Reconnecting.')
        utils.send_sms(f'Twitter API connection failed with status code {status}. Reconnecting.')
        raise ConnectionError(status)


@backoff.on_exception(backoff.expo, ConnectionError, max_tries=8,
                      on_giveup=lambda x: utils.send_sms('Giving up reconnecting after 8 tries. App down.'))
def connect_stream(
        auth: OAuthHandler,
        tweet_handler_map: Dict[str, utils.TweetHandler],
        time_limit: Optional[int],
        batch_size: int = 20,
        write_to_file: bool = True
):
    """Creates a stream listener and begins listening for incoming tweets.
    Uses the backoff package to attempt reconnection with exponential backoff on rate limits.

    Args:
        auth: authenticated Twitter API object
        tweet_handler_map: dict, question starts from q_starts.py to track
        time_limit: int or None, amount of time to keep the stream open. Setting to None listens indefinitely
        batch_size: int, number of tweets to hold in memory before parsing. In v1 without multiprocessing, this is set
            low by default so that the parsing and writing doesn't block getting additional stream data.
        write_to_file: bool, whether to write tweets to a file. Can set False for testing purposes.
    """
    # Create a new listener and stream
    logger.info('Creating Listener and Stream')
    agent = Listener(tweet_handler_map, time_limit, batch_size=batch_size, write_to_file=write_to_file)
    t_stream = Stream(auth, agent)

    # Begin streaming
    logger.info('Beginning streaming')
    tracking = utils.get_full_tracking_list(tweet_handler_map)
    t_stream.filter(track=tracking)


def stream(
        q_list_names: Union[List[str], str],
        logger_filename: str = 'qs.log',
        logger_level: str = 'info',
        time_limit: Optional[int] = None,
        batch_size: int = 50,
        write_to_file: bool = True,
):
    """Main function. Authorizes API object, creates a logger, parses questions to track, and kicks off stream listener.

    Args:
        q_list_names: str or a list of strings, key(s) to fetch the question list(s) and output name(s) from q_starts.py
        logger_filename: str, name for logfile
        logger_level: str, level for reporting logging
        time_limit: int or None, amount of time to keep the stream open. Setting to None listens indefinitely
        batch_size: int, number of tweets to hold in memory before parsing. In v1 without multiprocessing, this is set
            low by default so that the parsing and writing doesn't block getting additional stream data.
        write_to_file: bool, whether to write tweets to a file. Can set False for testing purposes.

    Returns:
        True if all goes well and the function ends normally
    """
    auth = utils.get_auth()

    # Set logger
    global logger
    logger = log.set_log_config(logger_filename, logger_level)

    # Get the tweet handling objects
    q_list_names = [q_list_names] if not isinstance(q_list_names, list) else q_list_names
    tweet_handler_map = utils.get_tweet_handler_map(q_list_names, batch_size, write_to_file)

    # Connect to a stream using exponential backoff in the event of a connection error
    connect_stream(auth, tweet_handler_map, time_limit, batch_size=batch_size, write_to_file=write_to_file)

    return True


if __name__ == '__main__':
    fire.Fire(stream)
