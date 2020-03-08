"""
Scratch module for running code
"""
from dotenv import load_dotenv

from question_seeker import stream as streamer


load_dotenv()


if __name__ == '__main__':
    streamer.stream(
        q_list_names='imperative',
        time_limit=60,
    )
