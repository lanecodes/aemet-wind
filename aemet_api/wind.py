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
from typing import List, Optional

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
