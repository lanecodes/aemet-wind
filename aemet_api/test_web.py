"""
test_web.py
~~~~~~~~~~~
"""
import time
from typing import Tuple

from aemet_api.web import delay

def test_delay():
    """Check trival function takes at least delay time to run."""
    time1 = time.time()
    res = delay(1)(_dummy_func)(2)
    time2 = time.time()
    assert res == (2, 4)
    assert time2 - time1 >= 1


def _dummy_func(a: int) -> Tuple[int, int]:
    """Simple function which receives and returns data."""
    return a, a**2
