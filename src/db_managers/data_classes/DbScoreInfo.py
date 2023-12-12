import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ossapi import Score, serialize_model, Mod

from db_managers.data_classes import DbUserInfo


@dataclass
class DbScoreInfo:
    """
    Dataclass to wrap up and store the row entry of the 'scores' database table.
    """

    id: Optional[int]
    user_info_id: int
    score_json_data: str
    mods: Mod
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_row(cls, row):
        _id, _user_info_id, _score_json_data, _mods, _timestamp = row
        return cls(id=_id,
                   user_info_id=_user_info_id,
                   score_json_data=_score_json_data,
                   mods=Mod(_mods))

    @classmethod
    def from_score_and_user_info(cls, score_instance: Score, user_info: DbUserInfo):
        # Creates a new DbScoreInfo instance using data from the Score and DbUserInfo instances.
        return cls(id=None,
                   user_info_id=user_info.discord_user_id,
                   score_json_data=serialize_model(score_instance),
                   mods=score_instance.mods)

    def deserialize_score_json(self) -> dict:
        return json.loads(self.score_json_data)

    @staticmethod
    def deserialize_score_json_static(score_json_data: str):
        return json.loads(score_json_data)
