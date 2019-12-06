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


class AemetHttpError(Exception):
    """Exception arising when dealing with AEMET API."""
    def __init__(self, descripcion: str, estado: int) -> None:
        self.descripcion = descripcion
        self.estado = estado

    def __repr__(self):
        return (f'AemetHttpError(estado: {self.estado}, '
                f'descripcion: {self.descripcion}')

    def __str__(self):
        return (f'HTTP error code: {self.estado}\n'
                f'description: {self.descripcion}')


def get_response(endpoint_url: str) -> APIResponse:
    """Get a response from the AEMET API using the given endpoint URL.

    If there is an error, the API will just send back some JSON stating that
    there is an error, so requests.get(...).raise_for_status() won't raise a
    requests.exceptions.HTTPError. Instead we actually parse the returned JSON,
    and if it turns out there was an error we raise our own AemetHttpError
    exception.
    """
    r = requests.get(endpoint_url)
    response = r.json()

    if response['estado'] != 200:
        raise AemetHttpError(response['descripcion'], response['estado'])

    return APIResponse(
        r.json()['descripcion'],
        r.status_code,
        r.json()['datos'],
        r.json()['metadatos'],
    )
