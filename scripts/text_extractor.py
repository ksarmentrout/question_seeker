import datetime
import json
import os
import random
import string
from typing import (
    Optional,
)

import fire
import pandas as pd


def clean_tweet(tweet: str) -> str:
    """
    Remove a few weird unicode characters

    Args:
        tweet: tweet text

    Returns:
        Cleaned tweet
    """
    # Remove smart quotes
    tweet = tweet.replace(u'\u201c', '"').replace(u'\u201d', '"')

    # Remove smart apostrophe
    tweet = tweet.replace(u'\u2019', "'")

    # Ampersand encodings
    tweet = tweet.replace('&amp;', '&')

    # Remove newline
    tweet = tweet.replace('\n', ' ')

    return tweet


def write_tweets(
        tweets: pd.DataFrame,
        output_fn: str,
        append: bool = False,
        indent: bool = False,
):
    """
    Saves tweets to a json file

    Args:
        tweets: DataFrame of tweet info
        output_fn: output filename
        append: if True, appends new tweets to the existing file at `output_fn`
        indent: if True, adds indenting formatting to json file
    """
    # Open existing file and append new tweets
    if append:
        df = pd.read_json(output_fn)
        tweets = pd.concat([df, tweets])

    # Remove duplicates
    tweets = tweets[~tweets.duplicated('tweet_id')]

    # Save
    with open(output_fn, 'w', encoding='utf-8') as file:
        if indent:
            tweets.to_json(file, force_ascii=False, orient='records', indent=4)
        else:
            tweets.to_json(file, force_ascii=False, orient='records')


def extract_tweet_info(
        input_fn: str,
        output_fn: str,
        append: bool = False,
        make_copies: bool = True,
):
    """
    Extracts the body of the tweet from the massive dict of metadata
    that Twitter provides. If the tweet is long enough, it is stored in
    the `extended_tweet` field (added after the switch to 280 chars).

    Args:
        input_fn: input json filename containing full tweet info as dictionaries
        output_fn: output filename
        append: if True, appends new tweets to the existing file at `output_fn`
        make_copies: if True, writes one copy of the tweets to an `all_tweets` folder and another copy to a
            `pending_curation` folder for human curation
    """
    # Check that input file is actually there
    if not os.path.exists(input_fn):
        raise FileNotFoundError(f'No file found named {input_fn}')

    tweets = []

    with open(input_fn) as file:
        for line in file:
            tdict = json.loads(line)
            if 'extended_tweet' in tdict:
                tweet = tdict['extended_tweet']['full_text']
            else:
                tweet = tdict['text']

            tweet = clean_tweet(tweet)

            # Get location info if available
            if tdict.get('place') is not None:
                tweetplace = tdict['place']
                loc_name = tweetplace.get('full_name')
                country = tweetplace.get('country_code')
            else:
                loc_name = ''
                country = ''

            # Make a random slug for the URL permalink
            # This isn't cryptographically secure, but it doesn't have to be
            slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

            tweet_dict = {
                'tweet_text': tweet,
                'tweet_id': tdict['id_str'],
                'tweet_timestamp': tdict['created_at'],
                'loc_name': loc_name,
                'country': country,
                'permalink_slug': slug,
            }

            tweets.append(tweet_dict)

    # Make into a dataframe
    df = pd.DataFrame(tweets)

    # Save tweets
    if make_copies:
        # First do all_tweets
        all_tweets_output_fn = f'all_tweets/{output_fn.replace(".json", "_all.json")}'
        write_tweets(df, all_tweets_output_fn, append)

        # Write them again to a pending_curation folder (indent for human readability)
        pending_curation_fn = f'pending_curation/{output_fn}'
        write_tweets(df, pending_curation_fn, append, indent=True)
    else:
        write_tweets(df, output_fn, append)


def handler(
        input_fn: str,
        output_fn: Optional[str] = None,
        append: bool = False,
        make_copies: bool = True,
):
    """
    Make some runtime sanity checks and then call the text extractor.

    Args:
        input_fn: input filename - must be json.
        output_fn: optional output filename
        append: if True, appends new tweets to the existing file at `output_fn`
        make_copies: if True, writes one copy of the tweets to an `all_tweets` folder and another copy to a
            `pending_curation` folder for human curation
    """
    # Check that input fn in json
    if not input_fn.endswith('.json'):
        raise RuntimeError(f'Input function must be a json file. Got "{input_fn}"')

    # Create output filename if none was passed
    if output_fn is None:
        output_fn = input_fn.replace('.json', '')
        if output_fn.endswith('tweets'):
            output_fn = output_fn[:-6] + 'texts'

        # Add the date and a random slug to the filename
        # Today formatted as MMDDYYYY
        today = datetime.date.today().strftime('%m%d%Y')
        rand_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        output_fn += f'_{today}_{rand_slug}.json'

    # Make sure that if we want to append new tweets to a file, the output file exists
    if append:
        if not os.path.exists(output_fn):
            raise FileNotFoundError(
                f'To append to a file, the output file needs to exist. File path "{output_fn}" does not exist.'
            )

    extract_tweet_info(
        input_fn,
        output_fn,
        append,
        make_copies,
    )


if __name__ == '__main__':
    fire.Fire(handler)
