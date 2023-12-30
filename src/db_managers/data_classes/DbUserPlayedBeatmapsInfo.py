from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Type

from ossapi import GameMode, BeatmapCompact

from db_managers.data_classes import DbUserInfo

if TYPE_CHECKING:
    from db_managers.models.models import UserPlayedBeatmapsTable


@dataclass
class DbUserPlayedBeatmapsInfo:
    """
    Dataclass to wrap up and store the row entry of the 'user_played_beatmaps' database table.
    """

    id: Optional[int]
    user_info_id: int
    beatmap_id: int
    beatmapset_id: int
    mode: GameMode

    @classmethod
    def from_row(cls, row: 'UserPlayedBeatmapsTable'):
        return cls(id=row.id,
                   user_info_id=row.user_info_id,
                   beatmap_id=row.beatmap_id,
                   beatmapset_id=row.beatmapset_id,
                   mode=row.mode)

    @classmethod
    def from_beatmap_and_user_info(cls, beatmap: Type[BeatmapCompact], user_info: DbUserInfo):
        return cls(id=None,
                   user_info_id=user_info.discord_user_id,
                   beatmap_id=beatmap.id,
                   beatmapset_id=beatmap.beatmapset_id,
                   mode=beatmap.mode)
