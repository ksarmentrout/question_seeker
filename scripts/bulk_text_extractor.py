import os

import fire

from scripts import text_extractor


def bulk_extraction(
        dirname: str,
):
    """
    Bulk extracts tweets from any json file in the given directory

    Args:
        dirname: directory to search for files in
    """
    for filename in os.listdir(dirname):
        if not filename.endswith('.json'):
            continue

        fullpath = os.path.join(dirname, filename)
        text_extractor.handler(fullpath)


if __name__ == '__main__':
    fire.Fire(bulk_extraction)
