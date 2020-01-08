"""
wind.py
~~~~~~~

Extract data relevant to wind speeds from daily climate data.

The main objects to be aware of are the `DailyClimateQuery` class which
specifies the weather station id and date range of interest, and the
`get_daily_wind_speed_data` function which collects the data from a query and
returns it as an iterable over daily climate measurements for a specific
station. They are used like this::

>>> from datetime import date
>>> from aemet_api.secrets import API_KEY
>>> start_date, end_date = date(2019, 10, 1), date(2019, 11, 1)
>>> query = DailyClimateQuery('6293X', start_date, end_date)
>>> data = get_daily_wind_speed_data(query, API_KEY)
>>> data[0]
DailyWindData(station_id='6293X', date=datetime.date(2019, 10, 1), ave_wind_speed=3.6, max_gust=13.3, direction=27)
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, List, Optional, Union

import pandas as pd

from aemet_api.web import delay

from aemet_api.daily_climate import (
    DailyClimateData, DailyClimateQuery, DailyClimateQueryFunc,
    get_daily_climate_data, run_daily_climate_query
)


@dataclass
class DailyWindData:
    """Daily wind speed record.

    Parameters
    ----------
    station_id:
        Identifier for monitoring station. This corresponds to the 'indicativo'
        field returned in the station inventory data set (see stations.py).
    date:
        Date of observation. Called 'fecha' in the API response.
    ave_wind_speed:
        Average wind speed on `date` [m/s]. Called 'velmedia' in the API
        response.
    max_gust:
        Maximum wind gust on `date` [m/s]. Called 'racha' in the API response.
    direction:
        Direction of maximum gust. Units are 'tens of degree' (decenas de
        grado), i.e. multiply this value by 10 to get compass direction in
        degrees. Called 'dir' in the API response.
    """
    station_id: str
    date: date
    ave_wind_speed: Optional[float]
    max_gust: Optional[float]
    direction: Optional[int]


class BeaufortBounds:
    """Upper bounds for levels on the Beaufort wind force scale.

    The ith element of each of the attributes of this class corresponds to
    the upper bound of the wind speed which would be given a Beaufort number
    of i. e.g. the highest wind speed in km/h with a Beaufort number of 4 is
    given by::

        >>> beaufort_bounds = BeaufortBounds()
        >>> beaufort_bounds.km_per_h[4]
        28

    Similarly in m/s::

        >>> beaufort_bounds = BeaufortBounds()
        >>> beaufort_bounds.m_per_s[4]
        7.777777777777778

    Attributes
    ----------
    km_per_h (tuple):
        Beaufort bounds in km/h
    m_per_s (tuple):
        Beaufort bounds in m/s

    Notes
    -----
    See the `RMetS`_ website for information about the Beaufort scale, and
    as a reference for the data in this class definition.

    _`RMetS`: https://www.rmets.org/resource/beaufort-scale
    """
    def __init__(self):
        self.km_per_h = (1, 5, 11, 19, 28, 38, 49,
                         61, 74, 88, 102, 117, 118)
        self.m_per_s = tuple([x * 1000 / 3600 for x in self.km_per_h])


BEAUFORT_BOUNDS = BeaufortBounds()


def wind_data_for_sites(start_date: date, end_date: date,
                        site_ids: Iterable[str], API_KEY: str) -> pd.DataFrame:
    """Download wind data from AEMET API for sites between specified dates."""
    return pd.concat([
        pd.DataFrame([
            vars(day) for day in get_daily_wind_speed_data(
                DailyClimateQuery(site_no, start_date, end_date), API_KEY,
                delay(1)(run_daily_climate_query)
            )
        ])
        for site_no in site_ids
    ])


def get_daily_wind_speed_data(
        query: DailyClimateQuery,
        api_key: str,
        get_data_func: DailyClimateQueryFunc=None,
    ) -> List[DailyWindData]:
    """Retrieve daily wind speed data for a station and date range.

    Parameters
    ----------
    query:
        Query specifying weather station and date range to collect data for.
    api_key:
        AEMET API key.
    get_data_func (optional):
        Function to use to get data from the API. Defaults to
        `run_daily_climate_query` if `get_data_func` is None.

    Notes
    -----
    See documentation for `get_daily_climate_data` for an explanation of the
    motivation for allowing `get_data_func` to be user configurable.
    """
    if get_data_func is None:
        get_data_func = run_daily_climate_query
    return [
        DailyWindData(
            station_id=query.station_id,
            date=datetime.strptime(record['fecha'], '%Y-%m-%d').date(),
            ave_wind_speed=_process_wind_speed_field('velmedia', record),
            max_gust=_process_wind_speed_field('racha', record),
            direction=_process_wind_direction_field('dir', record),
        )
        for record in get_daily_climate_data(query, api_key, get_data_func)
    ]


def _process_wind_speed_field(field_name: str,
                              record: DailyClimateData) -> Optional[float]:
    """Convert wind speed value to float, handle missing data.

    Wind speed values are not required fields, so some None values are
    expected.
    """
    try:
        value = record[field_name]
    except KeyError:
        return None

    return float(value.replace(',', '.'))


def _process_wind_direction_field(field_name: str,
                                  record: DailyClimateData) -> Optional[int]:
    """Convert wind direction value to float, handle missing data.

    Wind speed values are not required fields, so some None values are
    expected.
    """
    try:
        value = record[field_name]
    except KeyError:
        return None

    return int(value)


def degrees_to_cardinal(deg: Union[int, float]) -> str:
    """Return cardinal direction given compass degrees."""
    directions = ['NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    lower_bound = 22.5
    for dir_ in directions[:-1]:
        upper_bound = lower_bound + 45
        if deg > lower_bound and deg <= upper_bound:
            return dir_
        lower_bound = upper_bound
    return directions[-1]


def beaufort_number(wind_speed: float) -> int:
    """Return Beaufort number for a given wind speed in m/s."""
    for i, upper_bound in enumerate(BEAUFORT_BOUNDS.m_per_s):
        if wind_speed <= upper_bound:
            return i
    return 12  # maximum possible Beaufort number for wind speed > 37 m/s
