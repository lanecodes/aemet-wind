"""
wind.py
~~~~~~~

Extract data relevant to wind speeds from daily climate data.

The main objects to be aware of here are the `DailyClimateQuery` class which
specifies the weather station id and date range of interest, and the
`get_daily_wind_speed_data` function which collects the data from a query and
returns it as an iterable over daily cliamte measurements for a specific
station. They are used like this::

>>> from datetime import date
>>> from aemet_wind.secrets import API_KEY
>>> start_date = date(1990, 1, 1)
>>> end_date =  date(2019, 11, 1)
>>> query = DailyClimateQuery('6293X', start_date, end_date)
>>> data = get_daily_wind_speed_data(query, API_KEY)
>>> data[0]
DailyWindSpeed(station_id='6293X', date=datetime.date(2009, 7, 19), ave_wind_speed=7.2, max_gust=17.2)
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

from aemet_wind.daily_climate import (
    DailyClimateData, DailyClimateQuery, get_daily_climate_data
)


@dataclass
class DailyWindSpeed:
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
    """
    station_id: str
    date: date
    ave_wind_speed: Optional[float]
    max_gust: Optional[float]


def get_daily_wind_speed_data(query: DailyClimateQuery,
                              api_key: str) -> List[DailyWindSpeed]:
    """Retrieve daily wind speed data for a station and date range."""
    return [
        DailyWindSpeed(
            station_id=query.station_id,
            date=datetime.strptime(record['fecha'], '%Y-%m-%d').date(),
            ave_wind_speed=_process_wind_speed_field('velmedia', record),
            max_gust=_process_wind_speed_field('racha', record),
        )
        for record in get_daily_climate_data(query, api_key)
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
