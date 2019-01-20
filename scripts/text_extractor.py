import json
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


if __name__ == '__main__':
    fire.Fire(extract_tweet_body)

