from typing import List, Tuple


all_starts = [
    'why am',
    'why are',
    'why can',
    "why can't",
    'why do',
    "why don't",
    'why is',
    'why must',
    'why should',
    'why did',
    'y am',
    'y are',
    'y can',
    "y can't",
    'y do',
    "y don't",
    'y is',
    'y must',
    'y should',
    'y did',
    'how should',
    'who should',
    'what should',
    'where should',
]


capacity_starts = [
    'why can',
    "why can't",
    'y can',
    "y can't",
]


categorizing_starts = [
    'why is',
    'y is'
]


factual_starts = [
    'why are',
    'why do',
    "why don't",
    'why did',
    'y are',
    'y do',
    "y don't",
    'y did',
]


imperative_starts = [
    'why must',
    'why should',
    'y must',
    'y should',
    'how should',
    'who should',
    'what should',
    'where should'
]


personal_starts = [
    'why am',
    'y am'
]


govt_starts = [
    'the government should',
    "why doesn't the government",
    "why does the government not",
    'trump should',
    "why doesn't trump",
    "why does trump not",
]

test_start = [
    'cat'
]


def get_q_list(q_list_name: str) -> List[str]:
    lookup = {
        'all': all_starts,
        'capacity': capacity_starts,
        'categorizing': categorizing_starts,
        'factual': factual_starts,
        'govt': govt_starts,
        'imperative': imperative_starts,
        'personal': personal_starts,
        'test': test_start
    }
    return lookup[q_list_name]


def get_q_list_and_filename(q_list_name: str) -> Tuple[List[str], str]:
    lookup = {
        'all': (all_starts, 'all_tweets.json'),
        'capacity': (capacity_starts, 'capacity_tweets.json'),
        'categorizing': (categorizing_starts, 'categorizing_tweets.json'),
        'factual': (factual_starts, 'factual_tweets.json'),
        'govt': (govt_starts, 'govt_tweets.json'),
        'imperative': (imperative_starts, 'imperative_tweets.json'),
        'personal': (personal_starts, 'personal_tweets.json'),
        'test': (test_start, 'tweets.json')
    }
    return lookup[q_list_name]
