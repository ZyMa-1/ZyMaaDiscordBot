from dataclasses import dataclass

from ossapi import GameMode

from db_managers import conversion_utils


@dataclass
class DbUserInfo:
    """
    Dataclass to wrap up and store the row entry of the 'users' database table.
    """

    discord_user_id: int
    osu_user_id: int
    osu_game_mode: GameMode

    @classmethod
    def from_row(cls, row):
        return conversion_utils.from_user_row(row)
