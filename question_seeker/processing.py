from itertools import chain
import json
import re
from typing import (
    Dict,
    List,
    Union,
)

from question_seeker.log import LOGGER as logger
from question_seeker import q_starts, utils


PATTERN = r"(\b(why|y|who|what|where|how)\b \b(am|are|can|can't|did|do|don't|is|must|should)\b) .+\?"
R = re.compile(PATTERN, flags=re.IGNORECASE)


GOVT_PATTERNS = [
    r"(\b(the government|trump)\b should) .+",
    r"(\b(why doesn't) \b(the government|trump)\b) .+",
    r"(\b(why does) \b(the government|trump)\b not) .+",
]
GOVT_RS = [re.compile(x, flags=re.IGNORECASE) for x in GOVT_PATTERNS]


class TweetHandler:
    def __init__(self, starts: List[str], filename: str, batch_size: int, write_to_file: bool):
        self.starts = starts
        self.filename = filename
        self.file = utils.FileWrapper(self.filename)
        self.batch_size = batch_size
        self.write_to_file = write_to_file
        self.bucket = []

    def add_tweet(self, tweet: str):
        """
        Adds a tweet to the handler bucket

        Args:
            tweet: tweet text
        """
        self.bucket.append(tweet)
        if len(self.bucket) >= self.batch_size:
            if self.write_to_file:
                self.write_tweets()
            self.bucket = []

    def write_tweets(self):
        """
        Writes stored tweets to the file stored in the handler
        """
        for tweet in self.bucket:
            self.file.write(tweet)
        logger.debug(f'Wrote {len(self.bucket)} tweets to file')

    def __repr__(self):
        return f'TweetHandler with filename "{self.filename}" holding {len(self.bucket)} tweets'


def get_tweet_handler_map(
        q_list_names: List[str],
        batch_size: int,
        write_to_file: bool
) -> Dict[str, TweetHandler]:
    """
    Creates a dictionary from question start to TweetHandler object for each question start matching the
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
    """
    Checks if a string is asking a question that is being tracked.
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

    logger.debug(f'String to parse: {tweet_text}')
    match = R.search(tweet_text)

    # Try govt list
    if not match:
        for GOVT_R in GOVT_RS:
            match = GOVT_R.search(tweet_text)
            if match:
                break

    if match:
        logger.debug(f'Match groups: {match.groups()}')
        q_lead = match.groups()[0].rstrip()
        logger.debug(f'Question lead: {q_lead}')
        logger.debug(f'Tweet handler map keys: {tweet_handler_map.keys()}')
        if q_lead.lower() in tweet_handler_map:
            tweet_handler_map[q_lead.lower()].add_tweet(json.dumps(tweet))
            logger.debug(f'Added tweet to handler {tweet_handler_map[q_lead.lower()]}')
    else:
        logger.debug('No match')


def process_tweets(
        tweet_list: List[dict],
        tweet_handler_map: Dict[str, TweetHandler],
        force_write: bool = False
):
    """
    Filters a batch of collected tweets for the presence of one of the tracked questions, adding relevant tweets
    to the appropriate TweetHandler object via the add_tweet() method.

    Args:
        tweet_list: list of tweet objects as dictionaries
        tweet_handler_map: mapping of question starts to TweetHandler objects
        force_write: bool, whether to force all tweet handlers to write their held tweets to file
    """
    for tweet in tweet_list:
        process(tweet, tweet_handler_map)

    if force_write:
        for tweet_handler in list(set(tweet_handler_map.values())):
            tweet_handler.write_tweets()
