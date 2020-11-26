from pathlib import Path
import random
import string

import fire
import numpy as np
import pandas as pd

from question_seeker import utils


def take_bite(
    input_fn: str,
    output_dir: str,
    bite_size: int = 50,
):
    '''
    This function takes a random selection of tweets within a json file and separates them out into 
    two other easily-curated files. 

    The input function must be json. The outputs are one file with all tweet data available (suffixed
    with 'texts'), and another (suffixed with 'strings') with only the tweet bodies for easy curation. 

    '''
    df = pd.read_json(input_fn)

    df_len = len(df)
    mask = [False] * df_len
    rand_indices = random.sample(list(range(df_len)), k=bite_size)
    for idx in rand_indices:
        mask[idx] = True
    
    mask = np.asarray(mask)
    sample = df[mask].copy()
    assert len(sample) == bite_size

    df = df[~mask]
    assert len(df) == df_len - bite_size
    utils.encoded_write(df, input_fn)

    slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

    filename = Path(input_fn).resolve().parts[-1]
    output_text_filename = f'texts_{filename.replace(".json", "")}_{slug}.json'
    output_strings_filename = f'strings_{filename.replace(".json", "")}_{slug}.csv'

    # Make sure we're putting the output files in the output dir
    output_text_fn = str(Path(output_dir).resolve() / output_text_filename)
    output_strings_fn = str(Path(output_dir).resolve() / output_strings_filename)

    strings = sample.tweet_text.values.tolist()

    utils.encoded_write(sample, output_filename=output_text_fn)

    with open(output_strings_fn, 'w', encoding='utf-8') as file:
        for line in strings:
            file.write(line)
            file.write('\n')


if __name__ == '__main__':
    fire.Fire(take_bite)
