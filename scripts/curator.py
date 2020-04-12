import json
import os
from typing import (
    Dict,
    List,
    Optional,
)

import fire

from question_seeker import utils


def curate(
        filename: str,
):
    """
    Opens a json file of tweets and provides only the tweet on a prompt
    for easy curation.

    Args:
        filename: file of tweets to prune
    """
    with open(filename) as file:
        data = json.load(file)

    def save_tweets(
            tweets: List[Dict],
            suffix: Optional[str] = None,
    ):
        if suffix is not None:
            write_filename = filename.replace('.json', suffix)
        else:
            write_filename = filename

        utils.encoded_write(tweets, write_filename, indent=True)

    kept_tweets = []
    total_tweets = len(data)
    save_and_quit = False
    for counter, tweet in enumerate(data):
        resp = input(f"{tweet['tweet_text']} ([n]/y/s/u) ({counter}/{total_tweets}): ").lower()

        if resp == 'y':
            # Keep the tweet
            kept_tweets.append(tweet)
        elif resp == 's':
            save_and_quit = True
            break
        elif resp == 'u':
            # This is an undo button. It can only be used to go back a single line for now.
            print('Returning to previous tweet...')
            prev_tweet = data[counter - 1]

            # Only give n/y options
            new_resp = input(f"{prev_tweet['tweet_text']} ([n]/y) ({counter-1}/{total_tweets}): ").lower()

            if new_resp == resp:
                # If I want to do the same thing as before, just keep going
                continue
            elif new_resp == 'y':
                kept_tweets.append(prev_tweet)
            else:
                kept_tweets = kept_tweets[:-1]
        else:
            # By default, skip the tweet
            continue

    if save_and_quit:
        # Find the next unique progress marker filename
        save_suffix = f'_intermediate_progress_20.json'
        progress_counter = 0
        while progress_counter < 20:
            save_suffix = f'_intermediate_progress_{progress_counter}.json'
            if not os.path.exists(filename.replace('.json', save_suffix)):
                break
            progress_counter += 1
        if progress_counter == 20:
            print(
                "Out of saves! I'll still save this one but seriously, "
                "just commit to finishing this file, ok? Next time it'll "
                "overwrite something important."
            )

        # Save the curated tweets in a new file
        save_tweets(kept_tweets, save_suffix)

        # Save the remaining tweets in the original file location
        remaining_tweets = data[counter + 1:]
        save_tweets(remaining_tweets)
    else:
        # Otherwise, curation is over so we can just save all the tweets in the original location
        save_tweets(kept_tweets)


if __name__ == '__main__':
    fire.Fire(curate)
