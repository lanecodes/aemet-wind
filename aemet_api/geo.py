"""
geo.py
~~~~~~

Functions used to identify AEMET stations in desired geographic locations.
"""
from typing import Union

from shapely.geometry import Point

import pandas as pd
import geopandas as gpd


def aemet_stations_to_gdf(df: pd.DataFrame, lat_col: str='latitud',
                          lon_col: str='longitud') -> gpd.GeoDataFrame:
    """Construct GeoDataFrame from AEMET station data.

    Returned geographic data is in the EPSG:2062 coordinate reference system
    (CRS) for Madrid 1870 (Madrid) / Spain. This has the advantage over WGS84
    of having units of meters, simplifying subsequent distance-based
    analysis.

    Parameters
    ----------
    df:
        DataFrame containing geographic information about AEMET stations
        with latitude/ longitude data encoded as per the AEMET API.
    lat_col:
        Name of column containing latitude data (optional)
    lon_col:
        Name of column containing longitude data (optional)
    """
    _check_lat_lon_codings(df, lat_col, lon_col)
    return gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy
                  in zip(decode_lat_lon(df[lon_col]),
                         decode_lat_lon(df[lat_col]))],
        crs={'init': 'epsg:4326'}
    ).to_crs(epsg=2062)


def _check_lat_lon_codings(df: pd.DataFrame, lat_col: str='latitud',
                           lon_col: str='longitud') -> None:
    """Check some assumptions about the way lat/lon are encoded in AEMET.

    Hypothesis is that `latitud` and `longitud` are coded such that the last
    letter is direction WRT Geodetic origin (intersection of equator and
    prime meridian), i.e. N, S, E, W, and the preceeding 6 digit number
    should be divided by 10000 to obtain decimal coordinates.

    Parameters
    ----------
    df:
        DataFrame containing AEMET station data
    lat_col:
        Name of column containing latitude data (optional)
    lon_col:
        Name of column containing longitude data (optional)
    """
    def check_lat_lon_codes_have_length_7(df: pd.DataFrame) -> None:
        for coord in [lat_col, lon_col]:
            assert (df[coord].str.len() == 7).all(), (
                f'Found some {coord} entries without 7 characters.'
            )

    def check_lat_end_in_N_or_S(df: pd.DataFrame) -> None:
        assert (df[lat_col].str[-1].isin(['N', 'S'])).all(), (
            'Not all latitudes and in N or S'
        )

    def check_lon_end_in_E_or_W(df: pd.DataFrame) -> None:
        assert (df[lon_col].str[-1].isin(['E', 'W'])).all(), (
            'Not all longitudes and in E or W'
        )

    check_lat_lon_codes_have_length_7(df)
    check_lat_end_in_N_or_S(df)
    check_lon_end_in_E_or_W(df)


def decode_lat_lon(s: pd.Series) -> pd.Series:
    """Convert AEMET coded latitude/ longitude to decimal."""
    def direction_code_to_sign(x: str) -> int:
        """If west of meridian or south of equator make sign negative."""
        n, code = int(x[:-1]), x[-1]
        n = n * -1 if code in ['S', 'W'] else n
        return n

    def integer_to_float(x: int) -> float:
        """Divide integer quantity by 10000 to find decimal coordinate."""
        return x / 10000

    return s.transform(direction_code_to_sign).transform(integer_to_float)


def stations_near_targets(station_gdf: gpd.GeoDataFrame,
                          target_gdf: gpd.GeoDataFrame,
                          max_dist: Union[int, float]) -> gpd.GeoDataFrame:
    """GeoDataFrame of AEMET stations near target locations.

    Parameters
    ----------
    station_gdf:
        GeoDataFrame whose geometry column contains AEMET station location
        point data.
    target_gdf:
        GeoDataFrame whose geometry column contains point data corresponding
        to the targets for which we would like to locate nearby AEMET
        stations.
    max_dist:
        Maximum distance in meters between targets and AEMET stations to
        include in results. I.e. AEMET stations further away from a target
        than this distance will be excluded.
    """
    buffered_target_gdf = target_gdf.copy()
    buffered_target_gdf['geometry'] = target_gdf['geometry'].buffer(max_dist)
    return gpd.sjoin(station_gdf, buffered_target_gdf, how='inner',
                     op='within')
