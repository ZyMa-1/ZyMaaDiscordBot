import json
from typing import Type

from ossapi.utils import Model


def deserialize_model(model_type: Type[Model], json_str: str):
    """
    Deserializes 'json_str' back to the ossapi model.

    Example:
    deserialize_model(Score, serialize_model(score_model_instance)) -> score_model_instance

    Yeah, dumb, I know.
    """
    # Load JSON string into a dictionary
    json_data = json.loads(json_str)

    # Create an instance of the specified model_type class
    try:
        model_instance = model_type(**json_data)
        return model_instance
    except Exception as e:
        # Re-raising the exception
        raise e
