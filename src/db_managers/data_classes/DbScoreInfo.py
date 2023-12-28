import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TYPE_CHECKING, Type

from ossapi import serialize_model, Mod, Score

from db_managers.data_classes import DbUserInfo

if TYPE_CHECKING:
    from db_managers.models.models import ScoreTable


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
    def from_row(cls, row: Type['ScoreTable']):
        return cls(id=row.id,
                   user_info_id=row.user_info_id,
                   score_json_data=row.score_json_data,
                   mods=row.mods,
                   timestamp=row.timestamp)

    @classmethod
    def from_score_and_user_info(cls, score_instance: Score, user_info: DbUserInfo):
        # Creates a new DbScoreInfo instance using data from the Score and DbUserInfo instances.
        return cls(id=None,
                   user_info_id=user_info.discord_user_id,
                   score_json_data=serialize_model(score_instance),
                   mods=score_instance.mods)

    def deserialize_score_json(self) -> dict:
        return json.loads(self.score_json_data)
