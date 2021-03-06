import datetime
import json
from pathlib import Path
import random
import string
from typing import Optional

import fire
import pandas as pd

from question_seeker import utils


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


def filter_for_curation(df: pd.DataFrame):
    """
    Filters tweets with commonly used phrases out from the body of tweets
    that will be curated.

    This should only be called when making two copies of the collected tweets.
    It is meant to be a time-saver for the curation process, not to remove
    tweets from the overall collected corpus.

    Right now this is done with exact matches, but could be updated later to
    use fuzzy string matching and scoring to account for tweets that contain
    similar and adjacent phrases.

    Args:
        df: dataframe holding tweets

    Returns:
        DataFrame with commonly seen tweets filtered out
    """
    def filter_tweet(tweet: str) -> bool:
        """
        Filtering function to run on individual tweets.
        Returns True if the tweet should be be kept, False otherwise.

        Args:
            tweet: body of the tweet to filter

        Returns:
            True if the tweet PASSES and does NOT contain any of the
            phrases below
        """
        keep_tweet = True

        phrase_list = [
            'what should i watch',
            'what should i watch next',
            'what should i do today',
            'what should i cook next',
            'what should i cook today',
            'what should i draw next',
            'netflix',
            'stream',
            'what should i eat? : ',
            'breakfast',
            'wear to the living room',
            '200 followers',
            '100 followers',
        ]
        lower_tweet = tweet.lower()
        if any([x in lower_tweet for x in phrase_list]):
            keep_tweet = False

        if lower_tweet == 'what should i do?':
            keep_tweet = False

        return keep_tweet

    df['keep'] = df.tweet_text.apply(filter_tweet)
    df = df[df.keep]
    df = df.drop('keep', axis=1)
    return df


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
    utils.encoded_write(tweets, output_fn, indent)


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
    full_input_fp = Path(input_fn)
    full_output_fp = Path(output_fn)
    base_outdir = full_output_fp.parent
    outname = full_output_fp.name

    # Check that input file is actually there
    if not full_input_fp.exists():
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
        Path(base_outdir / 'all_tweets').mkdir(parents=True, exist_ok=True)
        all_tweets_output_fn = str(base_outdir / f'all_tweets/{outname.replace(".json", "_all.json")}')
        write_tweets(df, all_tweets_output_fn, append)

        # Write them again to a pending_curation folder (indent for human readability)
        Path(base_outdir / 'pending_curation').mkdir(parents=True, exist_ok=True)
        pending_curation_fn = str(base_outdir / 'pending_curation' / outname)
        curation_df = filter_for_curation(df)
        write_tweets(curation_df, pending_curation_fn, append, indent=True)
    else:
        write_tweets(df, str(full_output_fp), append)


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

    full_input_fp = Path(input_fn).resolve()
    input_filename = full_input_fp.name
    root_fp = full_input_fp.parent

    # Create output filename if none was passed
    if output_fn is None:
        output_fn = input_filename.replace('.json', '').replace('tweets', 'texts')

        # Add the date and a random slug to the filename
        # Today formatted as MMDDYYYY
        today = datetime.date.today().strftime('%m%d%Y')
        rand_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        output_fn += f'_{today}_{rand_slug}.json'

        full_output_fp = root_fp / output_fn
    else:
        full_output_fp = Path(output_fn)

    # Make sure that if we want to append new tweets to a file, the output file exists
    if append:
        if not full_output_fp.exists():
            raise FileNotFoundError(
                f'To append to a file, the output file needs to exist. File path "{output_fn}" does not exist.'
            )

    extract_tweet_info(
        str(full_input_fp),
        str(full_output_fp),
        append,
        make_copies,
    )


if __name__ == '__main__':
    fire.Fire(handler)
