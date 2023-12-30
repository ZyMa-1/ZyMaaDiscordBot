from dataclasses import dataclass
from typing import TYPE_CHECKING

from ossapi import GameMode

if TYPE_CHECKING:
    from db_managers.models.models import UserTable


@dataclass
class DbUserInfo:
    """
    Dataclass to wrap up and store the row entry of the 'users' database table.
    """

    discord_user_id: int
    osu_user_id: int
    osu_game_mode: GameMode

    @classmethod
    def from_row(cls, row: 'UserTable'):
        return cls(discord_user_id=row.discord_user_id,
                   osu_user_id=row.osu_user_id,
                   osu_game_mode=row.osu_game_mode)
