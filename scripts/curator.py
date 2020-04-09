import json
import os
from typing import Dict, List, Optional

import fire


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

        with open(write_filename, 'w') as outfile:
            json.dump(tweets, outfile)

    kept_tweets = []
    total_tweets = len(data)
    save_and_quit = False
    for counter, tweet in enumerate(data):
        resp = input(f"{tweet['tweet_text']} ([y]/n/s) ({counter}/{total_tweets}: ").lower()

        if resp == 'n':
            # Skip the tweet
            continue
        elif resp == 's':
            save_and_quit = True
            break
        else:
            # By default, keep the tweet
            kept_tweets.append(tweet)

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
