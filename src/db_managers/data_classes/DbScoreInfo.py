import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ossapi import serialize_model, Mod, Score

from db_managers import conversion_utils
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
        return conversion_utils.from_score_row(row)

    @classmethod
    def from_score_and_user_info(cls, score_instance: Score, user_info: DbUserInfo):
        # Creates a new DbScoreInfo instance using data from the Score and DbUserInfo instances.
        return cls(id=None,
                   user_info_id=user_info.discord_user_id,
                   score_json_data=serialize_model(score_instance),
                   mods=score_instance.mods)

    def deserialize_score_json(self) -> dict:
        return json.loads(self.score_json_data)
