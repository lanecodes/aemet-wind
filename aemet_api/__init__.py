"""
aemet_api
~~~~~~~~~

Python interface to the AEMET OpenData REST API.
"""
import logging

from aemet_api.daily_climate import (
    DailyClimateData, DailyClimateQuery, get_daily_climate_data
)
from aemet_api.wind import DailyWindSpeed, get_daily_wind_speed_data

API_KEY_ADVICE = ('You will need to obtain your own API key from '
                  'https://opendata.aemet.es/centrodedescargas/inicio')
try:
    from aemet_api.secrets import API_KEY
except ModuleNotFoundError:
    logging.warning('No secrets module found. ' + API_KEY_ADVICE)
except ImportError:
    logging.warning('No API_KEY attribute found in secrets.py. '
                    + API_KEY_ADVICE)
