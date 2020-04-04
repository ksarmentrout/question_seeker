import json
import fire


def curate(
        filename: str,
        overwrite: bool = True,
):
    """
    Opens a json file of tweets and provides only the tweet on a prompt
    for easy curation.

    Args:
        filename: file of tweets to prune
        overwrite: if True, overwrites the original file with the curated tweets
    """
    with open(filename) as file:
        data = json.load(file)

    kept_tweets = []
    for tweet in data:
        resp = input(f"{tweet['tweet_text']} [y/n]").lower()

        if resp == 'y':
            kept_tweets.append(resp)

    if overwrite:
        write_filename = filename
    else:
        write_filename = filename.replace('.json', '_trimmed.json')

    with open(write_filename, 'w') as file:
        json.dump(kept_tweets, file)


if __name__ == '__main__':
    fire.Fire(curate)
