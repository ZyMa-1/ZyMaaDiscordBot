import json
from typing import Type

from ossapi.utils import Model


def deserialize_model(model_type: Type[Model], json_str: str):
    # Load JSON string into a dictionary
    json_data = json.loads(json_str)

    # Create an instance of the specified model_type class
    try:
        model_instance = model_type(**json_data)
        return model_instance
    except Exception as e:
        print(e)
