"""
stations.py
~~~~~~~~~~~

Get information about weather stations.
"""
import csv
from dataclasses import dataclass
from pathlib import Path
import logging
from typing import Dict, List

import requests

from aemet_wind.secrets import API_KEY
from aemet_wind.web import get_response

Station = Dict[str, str]


def get_station_inventory(api_key: str) -> List[Station]:
    """Get inventory of stations."""
    response = get_response(station_inventory_endpoint(api_key))
    return requests.get(response.data_url).json()


def station_inventory_endpoint(api_key: str) -> str:
    """URL for station inventory given API key.

    Referring to the `Accesso General`_ page, this corresponds to the dataset
    'Inventario de estaciones de Valores Climatológicos' under 'Valores
    Climatológicos'.

    .. _`Accesso General`: https://opendata.aemet.es/centrodedescargas/productosAEMET
    """
    return (
        'https://opendata.aemet.es/opendata/api/valores/climatologicos/'
        f'inventarioestaciones/todasestaciones/?api_key={api_key}'
    )


def station_inventory_to_csv(fname: str, stations: List[Station]) -> None:
    with open(fname, 'w') as csvfile:
        fieldnames = ['provincia', 'nombre', 'indicativo', 'latitud',
                      'longitud', 'altitud', 'indsinop']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

        writer.writeheader()
        writer.writerows(stations)


def output_path(fname: str) -> Path:
    """Output path for file name.

    Makes outputs/ directory if needed.
    """
    d = Path('outputs')
    d.mkdir(exist_ok=True)
    return d / fname


if __name__ == '__main__':
    station_inventory = get_station_inventory(API_KEY)
    station_inventory_to_csv(
        output_path('station_inventory.csv'), station_inventory
    )
