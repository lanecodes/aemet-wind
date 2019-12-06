# Notes

## Data provenance

`data/site_location_info.csv` comes from running
[EPDquery](https://zenodo.org/badge/latestdoi/225420303)

## Reason for not using Swagger Codegen client

I did originally attempt to use the `swagger_client`
[provided by AEMET][codegen] via Swagger Codegen to obtain the inventario de
estaciones (inventory of stations). However, with the following code in
`stations.py`...

```python
import logging
from pprint import pprint

import swagger_client
from swagger_client.rest import ApiException

from secrets import API_KEY

# Configure API key authorization: api_key
configuration = swagger_client.Configuration()
configuration.api_key['api_key'] = API_KEY

api = swagger_client.ValoresClimatologicosApi(
    swagger_client.ApiClient(configuration)
)

try:
    api_response = api.inventario_de_estaciones__valores_climatolgicos__with_http_info(async_req=False)
    pprint(api_response)
except ApiException as e:
    logging.error('Could not retrieve inventory of stations')
```

... I received this traceback:

```
Traceback (most recent call last):
  File "stations.py", line 25, in <module>
    api_response = api_instance.inventario_de_estaciones__valores_climatolgicos__with_http_info()
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api/valores_climatologicos_api.py", line 660, in inventario_de_estaciones__valores_climatolgicos__with_http_info
    collection_formats=collection_formats)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 322, in call_api
    _preload_content, _request_timeout)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 161, in __call_api
    return_data = self.deserialize(response_data, response_type)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 233, in deserialize
    return self.__deserialize(data, response_type)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 272, in __deserialize
    return self.__deserialize_model(data, klass)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 615, in __deserialize_model
    instance = klass(**kwargs)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/models/model200.py", line 57, in __init__
    self.estado = estado
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/models/model200.py", line 103, in estado
    raise ValueError("Invalid value for `estado`, must not be `None`")  # noqa: E501
ValueError: Invalid value for `estado`, must not be `None`
~/D/c/aemet_api $ python stations.py                      (aemet_api)
Traceback (most recent call last):
  File "stations.py", line 25, in <module>
    api_response = api_instance.inventario_de_estaciones__valores_climatolgicos__with_http_info(async_req=False)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api/valores_climatologicos_api.py", line 660, in inventario_de_estaciones__valores_climatolgicos__with_http_info
    collection_formats=collection_formats)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 322, in call_api
    _preload_content, _request_timeout)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 161, in __call_api
    return_data = self.deserialize(response_data, response_type)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 233, in deserialize
    return self.__deserialize(data, response_type)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 272, in __deserialize
    return self.__deserialize_model(data, klass)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/api_client.py", line 615, in __deserialize_model
    instance = klass(**kwargs)
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/models/model200.py", line 57, in __init__
    self.estado = estado
  File "/opt/miniconda3/envs/aemet_api/lib/python3.7/site-packages/swagger_client/models/model200.py", line 103, in estado
    raise ValueError("Invalid value for `estado`, must not be `None`")  # noqa: E501
ValueError: Invalid value for `estado`, must not be `None`
```

This error is related to the way the `Model200` constructor is called in
`api_client.py`, but given the current level of documentation for
`swagger_client` I don't hold much hope for debugging it.

[codegen]: https://opendata.aemet.es/centrodedescargas/codegen
