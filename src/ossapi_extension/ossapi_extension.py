from typing import Type

from ossapi import OssapiAsync
from ossapi.utils import Model


def deserialize_model(ossapi_instance: OssapiAsync, model_type: Type[Model], json_str: str):
    # Since ossapi does not have the explicit deserialization method,
    # I found something that looks like it should do the thing.
    return ossapi_instance._instantiate_type(json_str, model_type)
