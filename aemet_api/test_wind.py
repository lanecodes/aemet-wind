"""
test_wind.py
"""
from aemet_api.wind import degrees_to_cardinal, beaufort_number


def test_degrees_to_cardinal():
    assert degrees_to_cardinal(40) == 'NE'
    assert degrees_to_cardinal(80) == 'E'
    assert degrees_to_cardinal(140) == 'SE'
    assert degrees_to_cardinal(190) == 'S'
    assert degrees_to_cardinal(220) == 'SW'
    assert degrees_to_cardinal(275) == 'W'
    assert degrees_to_cardinal(310) == 'NW'
    assert degrees_to_cardinal(355) == 'N'
    assert degrees_to_cardinal(1) == 'N'


def test_beaufort_number():
    assert beaufort_number(0.25) == 0    # 0.9 km/h
    assert beaufort_number(20) == 8      # 72 km/h
    assert beaufort_number(30.6) == 11   # 110 km/h
    assert beaufort_number(41.7) == 12   # 150 km/h
