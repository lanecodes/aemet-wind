"""
stations.py
~~~~~~~~~~~

Get information about weather stations.
"""
import csv
from dataclasses import dataclass
from pathlib import Path
import logging
from typing import Dict, List, Union

import requests

from aemet_api.web import get_api_response

Station = Dict[str, str]
FieldDescr = Dict[str, Union[str, bool]]
MetaData = Dict[str, Union[str, List[FieldDescr]]]


def get_station_inventory(api_key: str) -> List[Station]:
    """Get inventory of stations."""
    response = get_api_response(station_inventory_endpoint(api_key))
    return requests.get(response.data_url).json()


def get_station_inventory_meta(api_key: str) -> MetaData:
    """Metadata for inventory of stations, field descriptions etc."""
    response = get_api_response(station_inventory_endpoint(api_key))
    return requests.get(response.metadata_url).json()


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


def station_inventory_to_csv(fname: Union[str, Path],
                             stations: List[Station]) -> None:
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
