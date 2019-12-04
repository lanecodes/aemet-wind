"""
web.py
~~~~~~~

Functions related to handling http requests.
"""
from dataclasses import dataclass
import logging

import requests

@dataclass
class APIResponse:
    description: str
    state: int
    data_url: str
    metadata_url: str


def get_response(endpoint_url: str) -> APIResponse:
    r = requests.get(endpoint_url)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        logging.error(
            f'HTTP error occurred while accessing endpoint {endpoint_url}'
        )
        raise

    return APIResponse(
        r.json()['descripcion'],
        r.status_code,
        r.json()['datos'],
        r.json()['metadatos'],
    )
