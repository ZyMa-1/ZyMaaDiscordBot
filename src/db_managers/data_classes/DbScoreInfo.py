import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from ossapi import serialize_model, Mod, Score, GameMode

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
    mode: GameMode
    beatmap_id: int
    timestamp: Optional[datetime]

    @classmethod
    def from_row(cls, row: 'ScoreTable'):
        return cls(id=row.id,
                   user_info_id=row.user_info_id,
                   score_json_data=row.score_json_data,
                   mods=row.mods,
                   mode=row.mode,
                   beatmap_id=row.beatmap_id,
                   timestamp=row.timestamp)

    @classmethod
    def from_score_and_user_info(cls, score_instance: Score, user_info: DbUserInfo):
        # Creates a new DbScoreInfo instance using data from the Score and DbUserInfo instances.
        return cls(id=None,
                   user_info_id=user_info.discord_user_id,
                   score_json_data=serialize_model(score_instance),
                   mods=score_instance.mods,
                   mode=score_instance.mode,
                   beatmap_id=score_instance.beatmap.id,
                   timestamp=None)

    def deserialize_score_json(self) -> dict:
        return json.loads(self.score_json_data)
