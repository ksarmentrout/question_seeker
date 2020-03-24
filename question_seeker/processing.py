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


# PATTERN = r"(\b(why|y|who|what|where|how)\b \b(am|are|can|can't|did|do|don't|is|must|should)\b) .+\?"

# For now, limit to just "imperative" starts
PATTERN = r"(\b(why|y|who|what|where|how)\b \b(must|should)\b) .+\?"
R = re.compile(PATTERN, flags=re.IGNORECASE)


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
        q_list_names: Union[List[str], str],
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


def process(
        tweet: dict,
        tweet_handler_map: Dict[str, TweetHandler],
        ignore_retweets: bool = True,
        ignore_replies: bool = True,
        ignore_links: bool = True,
):
    """
    Checks if a string is asking a question that is being tracked.
    Assumptions:
        - Looks throughout the entire tweet, not just the beginning.
        - Question must end with a question mark.
        - Case is ignored.

    Args:
        tweet: tweet to match against
        tweet_handler_map: mapping of question starts to TweetHandler objects
        ignore_retweets:
        ignore_replies:
        ignore_links:
    """
    # Ignore retweets
    # Only looking for original queries, not echoing other ideas, even if it indicates agreement.
    # Cuts down on redundancy of saved tweets.
    if ignore_retweets:
        if tweet.get('retweeted_status') is not None:
            return

    # Ignore direct replies to people
    # Only looking for questions posed to the general public, not to
    # specific people
    if ignore_replies:
        if tweet.get('in_reply_to_user_id') is not None:
            return

    media = tweet['entities']

    # Don't consider tweets with >2 hashtags.
    # Making the assumption that 3+ hashtags indicates engagement ploys
    # rather than seeking an actual answer.
    # if tweet_text.count('#') > 2:
    #     return
    if len(media['hashtags']) > 2:
        return

    # Don't consider tweets with >2 @ mentions.
    # Also making the assumption that 3+ mentions are engagement ploys
    # if tweet_text.count('@') > 2:
    #     return
    if len(media['user_mentions']) > 2:
        return

    # Ignore all media.
    # This includes both web links and attached images. I'm not planning on fetching and
    # rendering images or arbitrary links but don't want to present tweets without context,
    # so for now just ignore any tweets with external links.
    if ignore_links:
        if media['urls'] or media.get('media'):
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
