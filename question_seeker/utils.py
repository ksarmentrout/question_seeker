from itertools import chain
import json
import os
import re
import requests
import tweepy
from typing import Dict, List, TextIO, Union

from question_seeker.log import LOGGER as logger
from question_seeker import q_starts


PATTERN = r"(\b(why|y|who|what|where|how)\b \b(am|are|can|can't|did|do|don't|is|must|should)\b) .+\?"
R = re.compile(PATTERN, flags=re.IGNORECASE)


def send_sms(msg: str) -> int:
    """Sends an SMS notification via IFTTT webhook integration.

    Args:
        msg: str, body of the SMS

    Returns:
        int, status code of POST request
    """
    url = 'https://maker.ifttt.com/trigger/connection_failed/with/key/{}'.format(os.environ.get('IFTTT_KEY'))
    data = {"value1": msg}
    logger.info(f'Sending SMS with body "{msg}"')
    resp = requests.post(url, data=data)
    if not resp.ok:
        logger.error(f'Sending SMS failed with status code {resp.status_code}')
    return resp.status_code


def get_auth() -> tweepy.OAuthHandler:
    """Creates an authenticator object with the twitter API and tweepy.

    Returns:
        OAuthHandler object from tweepy for use in verifying requests
    """
    auth = tweepy.OAuthHandler(os.environ.get('CONSUMER_API_KEY'), os.environ.get('CONSUMER_API_SECRET_KEY'))
    auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))
    logger.info('Authenticated twitter API')
    return auth


class FileWrapper:
    def __init__(self, filename: str, mode: str='a'):
        """Wrapper for file handles to prevent multiple opens

        Args:
            filename: str, name of a file
            mode: str, how to open the file
        """
        self.filename = filename
        self.mode = mode
        self.file = open(self.filename, self.mode)
        self.isopen = True

    def open(self) -> TextIO:
        if self.isopen:
            return self.file
        self.file = open(self.filename, self.mode)
        self.isopen = True
        return self.file

    def close(self):
        if not self.isopen:
            return
        self.file.close()
        self.isopen = False

    def write(self, line: str):
        self.file.write(line + '\n')


class TweetHandler:
    def __init__(self, starts: List[str], filename: str, batch_size: int, write_to_file: bool):
        self.starts = starts
        self.filename = filename
        self.file = FileWrapper(self.filename)
        self.batch_size = batch_size
        self.write_to_file = write_to_file
        self.bucket = []

    def add_tweet(self, tweet: str):
        self.bucket.append(tweet)
        if len(self.bucket) >= self.batch_size:
            if self.write_to_file:
                self.write_tweets()
            self.bucket = []

    def write_tweets(self):
        for tweet in self.bucket:
            self.file.write(tweet)
        logger.debug(f'Wrote {len(self.bucket)} tweets to file')

    def __repr__(self):
        return f'TweetHandler with filename "{self.filename}" holding {len(self.bucket)} tweets'


def get_tweet_handler_map(q_list_names: Union[List[str], str], batch_size: int, write_to_file: bool)\
        -> Dict[str, TweetHandler]:
    """Creates a dictionary from question start to TweetHandler object for each question start matching the
    list of question titles passed in.

    Args:
        q_list_names: list of strings to fetch question starts from q_starts
        batch_size: int, number of tweets to hold onto before writing to a file
        write_to_file: bool, whether to actually write to a file

    Returns:
        Dictionary mapping of question starts to TweetHandler objects
    """
    handler_map = {}
    for name in q_list_names:
        tracking, filename = q_starts.get_q_list_and_filename(name)
        handler = TweetHandler(tracking, filename, batch_size, write_to_file)
        handler_map.update({start: handler for start in handler.starts})
    return handler_map


def get_full_tracking_list(tweet_handler_map: Dict[str, TweetHandler]) -> List[str]:
    tweet_handlers = list(set(tweet_handler_map.values()))
    return list(chain.from_iterable([x.starts for x in tweet_handlers]))


def process(tweet: dict, tweet_handler_map: Dict[str, TweetHandler]):
    """Checks if a string is asking a question that is being tracked.
    Assumptions:
        - Looks throughout the entire tweet, not just the beginning.
        - Question must end with a question mark.
        - Case is ignored.

    Args:
        tweet: tweet to match against
        tweet_handler_map: mapping of question starts to TweetHandler objects
    """
    # Ignore retweets
    # Only looking for original queries, not echoing other ideas, even if it indicates agreement.
    # Cuts down on redundancy of saved tweets.
    if tweet.get('retweeted_status'):
        return

    # Account for extended tweet field
    if tweet.get('extended_tweet'):
        tweet_text = tweet.get('extended_tweet', {}).get('full_text', '')
    else:
        tweet_text = tweet.get('text', '')

    # Remove newlines
    if '\n' in tweet_text:
        tweet_text = tweet_text.replace('\n', ' ')

    match = R.search(tweet_text)
    logger.debug(f'String to parse: {tweet_text}')

    if match:
        logger.debug(f'Match groups: {match.groups()}')
    else:
        logger.debug('No match')

    if match:
        q_lead = match.groups()[0].rstrip()
        logger.debug(f'Question lead: {q_lead}')
        logger.debug(f'Tweet handler map keys: {tweet_handler_map.keys()}')
        if q_lead.lower() in tweet_handler_map:
            tweet_handler_map[q_lead.lower()].add_tweet(json.dumps(tweet))
            logger.debug(f'Added tweet to handler {tweet_handler_map[q_lead.lower()]}')


def process_tweets(tweet_list: List[dict], tweet_handler_map: Dict[str, TweetHandler], force_write: bool=False):
    """Filters a batch of collected tweets for the presence of one of the tracked questions, adding relevant tweets
    to the appropriate TweetHandler object via the add_tweet() method.

    Args:
        tweet_list: list of tweet objects as dictionaries
        tweet_handler_map: mapping of question starts to TweetHandler objects
        force_write: bool, whether to force all tweet handlers to write their held tweets to file
    """
    for tweet in tweet_list:
        process(tweet, tweet_handler_map)

    if force_write:
        for tweet_handler in tweet_handler_map.values():
            tweet_handler.write_tweets()
