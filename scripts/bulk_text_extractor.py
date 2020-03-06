import pathlib

import fire

from scripts import text_extractor


def bulk_extraction(
        dirname: str,
        save_to_json: bool = False,
):
    """
    Bulk extracts tweets from any json file matching any of the question start keywords.

    Args:
        dirname: directory to search for files in
        save_to_json: whether to output files to json (otherwise .txt)
    """
    p = pathlib.Path.cwd() / dirname
    texts_path = p / 'texts'
    texts_path.mkdir(parents=True, exist_ok=True)

    for tweet_type in ['capacity', 'categorizing', 'factual', 'imperative', 'personal', 'govt']:
        print(f'Extracting {tweet_type} tweets')
        infile = p / f'{tweet_type}_tweets.json'

        if save_to_json:
            outfile = texts_path / f'{tweet_type}_texts.json'
        else:
            outfile = texts_path / f'{tweet_type}_texts.txt'

        text_extractor.extract_tweet_body(
            str(infile),
            str(outfile),
            save_to_json=save_to_json,
            append_to_json=False
        )


if __name__ == '__main__':
    fire.Fire(bulk_extraction)

