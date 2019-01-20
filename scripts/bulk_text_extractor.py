import json
import pathlib

import fire


def extract_tweet_body(input_fn, output_fn):
    outfile = open(output_fn, 'a')

    with open(input_fn) as file:
        for line in file:
            tdict = json.loads(line)
            if 'extended_tweet' in tdict:
                # print(tdict['extended_tweet'].keys())
                tweet = tdict['extended_tweet']['full_text']
            else:
                tweet = tdict['text']
            if '\n' in tweet:
                tweet = tweet.replace('\n', ' ')
            outfile.write(tweet + '\n')

    outfile.close()


def bulk_extraction(dirname):
    p = pathlib.Path.cwd() / dirname
    texts_path = p / 'texts'
    texts_path.mkdir(parents=True, exist_ok=True)

    for tweet_type in ['capacity', 'categorizing', 'factual', 'imperative', 'personal']:
        print(f'Extracting {tweet_type} tweets')
        infile = p / f'{tweet_type}_tweets.json'
        outfile = texts_path / f'{tweet_type}_texts.txt'
        extract_tweet_body(infile, outfile)


if __name__ == '__main__':
    fire.Fire(bulk_extraction)

