"""
daily_climate.py
~~~~~~~~~~~~~~~~

Functions which collect data from the AEMET endpoint corresponding to the
dataset 'Climatologías diarias' under 'Valores Climatológicos' (see
`Accesso General`_).

The API enforces a constraint that a single query can't cover a time span of
longer than 5 years. Much of the code here (most explicitly
`_time_decompose_query`) is concerned with accounting for this constraint.

The main objects to be aware of here are the `DailyClimateQuery` class which
specifies the weather station id and date range of interest, and the
`get_daily_climate_data` function which collects the data from a query and
returns it as an iterable over daily climate measurements for a specific
station. They are used like this::

>>> from datetime import date
>>> from aemet_api.secrets import API_KEY
>>> start_date = date(1990, 1, 1)
>>> end_date =  date(2019, 11, 1)
>>> query = DailyClimateQuery('6293X', start_date, end_date)
>>> data = get_daily_climate_data(query, API_KEY)
>>> type(data.__next__())  # data is an iterable
<class 'dict'>

.. _`Accesso General`: https://opendata.aemet.es/centrodedescargas/productosAEMET
"""
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import chain
import logging
from typing import Dict, Iterable, List

import requests

from aemet_api.web import  AemetHttpError, get_response

DailyClimateData = Dict[str, str]

MAX_YEARS = 5  # Maximum number of years a query can cover (limited by API)


@dataclass
class DailyClimateQuery:
    """Parameters specifying a station and date range for daily climate.

    Parameters
    ----------
    station_id:
        Identifier for monitoring station. This corresponds to the 'indicativo'
        field returned in the station inventory data set (see stations.py).
    start_date:
        First date for which data should be retrieved.
    end_date:
        Last date for which data should be retrieved.
    """
    station_id: str
    start_date: date
    end_date: date

    @property
    def years(self) -> float:
        """Number of years spanned by query."""
        return (self.end_date - self.start_date).days / 365


def get_daily_climate_data(query: DailyClimateQuery,
                           api_key: str) -> Iterable[DailyClimateData]:
    """Get daily climate data corresponding to query.

    Note
    ----
    If our query spans more than 5 years we will need to hit the API multiple
    times to gather the required data. Because each response is in the form
    List[DailyClimateData], once we've collected the data from all the
    responses we end up with a data structure like
    List[List[DailyClimateData]]. To flatten this structure without assigning
    a new, large list containing all the same information as the original
    nested lists we return an iterable which will keep producing data from the
    responses until we've processed it all. This is particularly useful in
    situations where we are only interested in a subset of the returned data.
    """
    time_decomposed_queries = _time_decompose_query(query)
    return chain(
        *[run_daily_climate_query(q, api_key) for q in time_decomposed_queries]
    )


def _time_decompose_query(query: DailyClimateQuery) -> List[DailyClimateQuery]:
    """Return list of queries whose time span fits within the API limit."""
    if query.years > MAX_YEARS:
        decomposed_queries = []
        start_date = query.start_date
        while True:
            end_date = start_date + timedelta(365 * MAX_YEARS)
            if end_date >= query.end_date:
                decomposed_queries.append(
                    DailyClimateQuery(query.station_id, start_date, query.end_date)
                )
                break
            decomposed_queries.append(
                DailyClimateQuery(query.station_id, start_date, end_date)
            )
            start_date = end_date + timedelta(1)

        return decomposed_queries

    return [query]


def run_daily_climate_query(query: DailyClimateQuery,
                            api_key: str) -> List[DailyClimateData]:
    """Query the API for daily climate data for given query.

    Notes
    -----
    Here we raise a ValueError if the time window specified by the query is
    greater than the maximum number of years allowed by the AEMET API.
    """
    if query.years > MAX_YEARS:
        raise ValueError(
            f'Queries run against the API can span a maximum of {MAX_YEARS} '
            f'years, but this query spans {query.years} years. Query: {query}'
        )
    try:
        response = get_response(daily_climate_endpoint(query, api_key))
    except  AemetHttpError as e:
        if e.descripcion == 'No hay datos que satisfagan esos criterios':
            logging.warning('No data found for query: ' + str(query))
            return []
        else:
            raise
    return requests.get(response.data_url).json()


def get_daily_climate_meta(query: DailyClimateQuery, api_key: str):
    """Get daily climate metadata for given query."""
    response = get_response(daily_climate_endpoint(query, api_key))
    return requests.get(response.metadata_url).json()


def daily_climate_endpoint(query: DailyClimateQuery, api_key: str) -> str:
    """URL for daily climate given API key.

    Referring to the `Accesso General`_ page, this corresponds to the dataset
    'Climatologías diarias' under 'Valores Climatológicos'.
    """
    start_date_str = _start_date_to_api_parameter(query.start_date)
    end_date_str = _end_date_to_api_parameter(query.end_date)

    return (
        'https://opendata.aemet.es/opendata/api/valores/climatologicos/'
        f'diarios/datos/fechaini/{start_date_str}/fechafin/{end_date_str}'
        f'/estacion/{query.station_id}/?api_key={api_key}'
    )


def _start_date_to_api_parameter(date: date) -> str:
    """Convert Python date to AEMET API start date parameter string."""
    return str(date) + 'T00:00:00UTC'


def _end_date_to_api_parameter(date: date) -> str:
    """Convert Python date to AEMET API end date parameter string."""
    return str(date) + 'T23:59:59UTC'
