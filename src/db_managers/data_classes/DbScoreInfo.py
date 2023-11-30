from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ossapi import Score, serialize_model, OssapiAsync

from db_managers.data_classes import DbUserInfo
from ossapi_extension import deserialize_model


@dataclass
class DbScoreInfo:
    """
    Dataclass to wrap up and store the row entry of the 'scores' database table.
    """

    id: Optional[int]
    user_info_id: int
    score_json_data: str
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_score_and_user_info(cls, score_instance: Score, user_info: DbUserInfo):
        # Creates a new DbScoreInfo instance using data from the Score and DbUserInfo instances.
        return cls(id=None, user_info_id=user_info.discord_user_id,
                   score_json_data=serialize_model(score_instance))

    def deserialize_score_json(self) -> Score:
        # Deserializes the 'Score' model from 'json_score_data' and returns it.
        return deserialize_model(Score, self.score_json_data)
