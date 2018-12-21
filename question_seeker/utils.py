import json
import logging
import os
import re
import requests
import tweepy
from typing import List, Union


logging.basicConfig(filename='qs.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)


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


def parse(s: str, tracking: List[str]) -> bool:
    """Checks if a string is asking a question that is being tracked.
    Assumptions:
        - Looks throughout the entire tweet, not just the beginning.
        - Question must end with a question mark.
        - Case is ignored.

    Args:
        s: tweet to match against
        tracking: List of question starts to check for (from q_starts.py)

    Returns:
        True if match is successful and question should be kept, False otherwise
    """
    # Ignore retweets (start with "RT")
    # Only looking for original queries, not echoing other ideas, even if it indicates agreement.
    # Cuts down on redundancy of saved tweets.
    if s[:3] == 'RT ':
        return False

    pattern = r"(\b(why|y|who|what|where|how)\b \b(am|are|can|did|do|don't|is|must|should)\b).+\?"
    r = re.compile(pattern, flags=re.IGNORECASE)
    match = r.search(s)
    logger.debug(f'String to parse: {s}')
    if match:
        logger.debug(f'Match groups: {match.groups()}')
    else:
        logger.debug('No match')

    if match:
        q_lead = match.groups()[0].rstrip()
        logger.debug(f'Question lead: {q_lead}')
        if q_lead.lower() in tracking:
            return True
    return False


def parse_tweets(tweets: List[dict], tracking: List[str]) -> List[str]:
    return [json.dumps(x) for x in tweets if parse(x.get('text', ''), tracking)]
