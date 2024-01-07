from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ossapi import GameMode

from factories import UtilsFactory

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
    _osu_game_mode: str
    _osu_user_name: Optional[str]

    @classmethod
    def from_row(cls, row: 'UserTable'):
        return cls(discord_user_id=row.discord_user_id,
                   osu_user_id=row.osu_user_id,
                   osu_game_mode=row.osu_game_mode,
                   _osu_game_mode=str(row.osu_game_mode.value),
                   _osu_user_name=None)

    @classmethod
    def from_args(cls, *args):
        discord_user_id = args[0]
        osu_user_id = args[1]
        osu_game_mode = args[2]
        return cls(discord_user_id=discord_user_id,
                   osu_user_id=osu_user_id,
                   osu_game_mode=osu_game_mode,
                   _osu_game_mode=str(osu_game_mode.value),
                   _osu_user_name=None)

    async def osu_user_name(self) -> Optional[str]:
        if self._osu_user_name:
            return self._osu_user_name

        osu_api_utils = UtilsFactory.get_osu_api_utils()
        user = await osu_api_utils.get_user(self.osu_user_id)
        if user:
            self._osu_user_name = user.username
            return self._osu_user_name
        return None
