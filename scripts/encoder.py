import os

import fire
import pandas as pd

from question_seeker import utils


def encode_json_file(
        filename: str,
        indent: bool = True,
):
    """
    Reads a json file and writes it out with the correct encoding.
    This is for any file that was accidentally written without it.

    Args:
        filename: filename to re-encode
        indent: whether to write out the file with indentation
    """
    if not filename.endswith('.json'):
        raise RuntimeError(f'Need to pass a json file. Got {filename}')

    df = pd.read_json(filename)
    utils.encoded_write(df, filename, indent)


def encode_dir(
        dirname: str,
        indent: bool = True,
):
    """
    Convenience function to run encode_json_file() on all json files
    in a directory.

    Args:
        dirname: directory containing json files to encode
        indent: whether to write out the file with indentation
    """
    if not os.path.isdir(dirname):
        raise NotADirectoryError(f'Path {dirname} is not a directory.')

    dir_contents = os.listdir(dirname)
    filenames = [x for x in dir_contents if x.endswith('.json')]

    for filename in filenames:
        encode_json_file(filename, indent)


if __name__ == '__main__':
    fire.Fire(
        {
            'dir': encode_dir,
            'file': encode_json_file,
        }
    )
