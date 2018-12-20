from typing import List


all_starts = [
    'why am',
    'why are',
    'why can',
    'why do',
    "why don't",
    'why is',
    'why must',
    'why should',
    'why did',
    'y am',
    'y are',
    'y can',
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

factual_starts = [
    'why are',
    'why do',
    "why don't",
    'why is',
    'why did',
    'y are',
    'y do',
    "y don't",
    'y is',
    'y did',
]

personal_starts = [
    'why am',
    'y am'
]

capacity_starts = [
    'why can',
    'y can',
]

imperative_starts = [
    'why can',
    'why do',
    "why don't",
    'why must',
    'why should',
    'y can',
    'y do',
    "y don't",
    'y must',
    'y should',
    'how should',
    'who should',
    'what should',
    'where should'
]

test_start = [
    'cat'
]


def get_q_list(q_list_name: str) -> List[str]:
    lookup = {
        'all': all_starts,
        'factual': factual_starts,
        'personal': personal_starts,
        'capacity': capacity_starts,
        'imperative': imperative_starts,
        'test': test_start
    }
    return lookup[q_list_name]
