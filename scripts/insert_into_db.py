import json
import os
from typing import (
    Any,
    List,
    Tuple,
)

import dotenv
import fire
import MySQLdb


dotenv.load_dotenv()

db = MySQLdb.connect(
    password=os.environ.get('MYSQL_DB_PASS'),
    db=os.environ.get('MYSQL_DB_NAME'),
    user=os.environ.get('MYSQL_DB_USER'),
    host=os.environ.get('MYSQL_DB_HOST'),
    charset='utf8mb4',
    use_unicode=True,
)
c = db.cursor()


def insert_tweets(
        input_filename: str,
        delete_file: bool = True,
        lines_per_commit: int = 20,
):
    with open(input_filename) as file:
        data = json.load(file)

    def do_execute(lines: List[Tuple[Any, ...]]):
        """
        Wrapper for bulk insert

        Args:
            lines: List of multiple tuples holding values to be inserted
        """
        sql_string = (
            """
            INSERT INTO tweet 
            (tweet_text, tweet_id, tweet_timestamp, loc_name, country, permalink_slug) 
            VALUES (%s, %s, %s, %s, %s, %s);
            """
        )

        # Commit, or rollback
        try:
            c.executemany(
                sql_string,
                lines,
            )
            db.commit()
            print('inserted')
        except:
            db.rollback()
            raise

    # Iterate over tweets in data json, committing groups at a time
    value_list = []
    for counter, line in enumerate(data):
        print(line)
        tup = (
            line['tweet_text'],
            line['tweet_id'],
            line['tweet_timestamp'],
            line['loc_name'],
            line['country'],
            line['permalink_slug'],
        )
        value_list.append(tup)

        if counter % lines_per_commit == 0:
            do_execute(value_list)
            value_list = []

    # Catch the remaining lines
    do_execute(value_list)

    if delete_file:
        os.remove(input_filename)


if __name__ == '__main__':
    fire.Fire(insert_tweets)
