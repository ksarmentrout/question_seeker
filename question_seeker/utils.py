import os
import requests
import tweepy
from typing import TextIO

from question_seeker.log import LOGGER as logger


GOVT_PATTERNS = [
    r"(\b(the government|trump)\b should .+",
    r"(\b(why doesn't) \b(the government|trump)\b .+",
    r"(\b(why does) \b(the government|trump)\b not .+",
]
GOVT_RS = [re.compile(x, flags=re.IGNORECASE) for x in GOVT_PATTERNS]


def send_email(msg: str) -> int:
    """
    Sends an email via IFTTT webhook integration.

    Args:
        msg: str, body of the email

    Returns:
        int, status code of POST request
    """
    url = f'https://maker.ifttt.com/trigger/qseek_post/with/key/{os.environ.get("IFTTT_KEY")}'
    data = {"value1": msg}
    logger.info(f'Sending email with body "{msg}"')
    resp = requests.post(url, data=data)
    if not resp.ok:
        logger.error(f'Sending email failed with status code {resp.status_code}')
    return resp.status_code


def get_auth() -> tweepy.OAuthHandler:
    """
    Creates an authenticator object with the twitter API and tweepy.

    Returns:
        OAuthHandler object from tweepy for use in verifying requests
    """
    auth = tweepy.OAuthHandler(os.environ.get('CONSUMER_API_KEY'), os.environ.get('CONSUMER_API_SECRET_KEY'))
    auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))
    logger.info('Authenticated twitter API')
    return auth


class FileWrapper:
    def __init__(self, filename: str, mode: str='a'):
        """
        Wrapper for file handles to prevent multiple opens

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
