import json
import os
from typing import (
    List,
    Optional,
)

import fire


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
        tweets: List[str],
        output_fn: str,
        save_to_json: bool = True,
        append_to_json: bool = False,
):
    tweet_json = {}
    if save_to_json and append_to_json:
        with open(output_fn) as readfile:
            tweet_json = json.load(readfile)

    file = open(output_fn, 'w')

    # Remove duplicates
    tweets = list(set(tweets))

    if save_to_json:
        if append_to_json:
            if isinstance(tweet_json.get('tweet'), list):
                tweet_json['tweet'].extend(tweets)
            else:
                tweet_json['tweet'] = tweets
        else:
            tweet_json = {'tweet': tweets}
        json.dump(tweet_json, file, indent=4, ensure_ascii=False)
    else:
        file.writelines(tweets)

    file.close()


def extract_tweet_body(
        input_fn: str,
        output_fn: str,
        save_to_json: bool = True,
        append_to_json: bool = False,
):
    """
    Extracts the body of the tweet from the massive dict of metadata
    that Twitter provides. If the tweet is long enough, it is stored in
    the `extended_tweet` field (added after the switch to 280 chars).

    Args:
        input_fn: input filename containing full tweet info dicts
        output_fn: output filename
        save_to_json: whether to save tweets as a json file (otherwise .txt)
        append_to_json: whether to append to existing json file structure or overwrite/create new
    """
    # Check that input file is actually there
    if not os.path.exists(input_fn):
        raise FileNotFoundError(f'No file found named {input_fn}')

    tweets = []
    include_newline = not save_to_json

    with open(input_fn) as file:
        for line in file:
            tdict = json.loads(line)
            if 'extended_tweet' in tdict:
                tweet = tdict['extended_tweet']['full_text']
            else:
                tweet = tdict['text']

            tweet = clean_tweet(tweet)
            if include_newline:
                tweet = tweet + '\n'

            tweets.append(tweet)

    # Save tweets
    write_tweets(tweets, output_fn, save_to_json, append_to_json)


def handler(
        input_fn: str,
        output_fn: Optional[str] = None,
        save_to_json: bool = True,
        append_to_json: bool = False,
):
    """
    Calls appropriate method based on json output preference.
    Default is to output json

    Args:
        input_fn: input filename
        output_fn: output filename
        save_to_json: whether to save tweets as a json file (otherwise .txt)
        append_to_json: whether to append to existing json file structure or overwrite/create new
    """
    # Create output filename if none was passed
    if output_fn is None:
        output_fn = input_fn[:input_fn.find('.')]
        if output_fn.endswith('tweets'):
            output_fn = output_fn[:-6] + 'texts'
        output_fn += '.json' if save_to_json else '.txt'

    extract_tweet_body(
        input_fn,
        output_fn,
        save_to_json,
        append_to_json,
    )


if __name__ == '__main__':
    fire.Fire(handler)

