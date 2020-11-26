import fire
import pandas as pd

from question_seeker import utils


def collapse_texts(
    texts_df_filename: str,
    strings_filename: str,
) -> str:
    '''
    This method expects two input filenames: one for a file with tweet texts and metadata, another for 
    a file of only strings of tweet bodies. 

    The use case is after curating the file of just tweet bodies, this method prunes the original 
    tweet texts json file to only retain those that are left in the strings file.
    '''
    df = pd.read_json(texts_df_filename)
    with open(strings_filename, encoding='utf-8') as file:
        data = [x.strip() for x in file.readlines()]
    
    df = df[df.tweet_text.isin(data)]
    collapsed_filename = texts_df_filename.replace('.json', '_collapsed.json')
    utils.encoded_write(df, collapsed_filename)

    return collapsed_filename


if __name__ == '__main__':
    fire.Fire(collapse_texts)
