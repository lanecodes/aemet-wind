from datetime import date

import pytest

from aemet_wind.daily_climate import DailyClimateQuery, _time_decompose_query

def test__time_decompose_query():
    """Test function which decomposes queries into 5 year chunks.

    The AEMET OpenData API refuses queries spanning more than 5 years, so we
    provide a function for breaking up queries longer than this into separate
    subqueries which will be subsequently recombined.
    """
    # 1st Jan 1990 -> 5th Oct 2009, spans 3 full and 1 partial 5-year chunks
    input_query = DailyClimateQuery('6297', date(1990, 1,1), date(2009, 10, 5))

    expected_output = [
        DailyClimateQuery('6297', date(1990, 1,1), date(1994, 12, 31)),
        DailyClimateQuery('6297', date(1995, 1,1), date(1999, 12, 31)),
        DailyClimateQuery('6297', date(2000, 1,1), date(2004, 12, 30)),  # leap year
        DailyClimateQuery('6297', date(2004, 12, 31), date(2009, 10, 5)),
    ]

    assert _time_decompose_query(input_query) == expected_output
