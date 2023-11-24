import dataclasses
from dataclasses import dataclass
from typing import Optional

from ossapi import GameMode


@dataclass
class DbUserInfo:
    """
    Dataclass to wrap up and store all entries of the 'users' database table.
    """
    discord_user_id: int
    osu_user_id: Optional[int]
    osu_game_mode: Optional[str]

    def is_config_set_up(self) -> bool:
        """
        Checks If all 'Optional' of the dataclass instance are not 'None'.
        """
        if None in dataclasses.asdict(self).values():
            return False

        return True

    def are_fields_valid(self) -> bool:
        """
        That is the one crutch, since 'osu_game_mode' should be in values of the 'GameMode' enum class,
        this method is used to check if it is okay.
        """
        if self.osu_game_mode not in [mode.value for mode in GameMode]:
            return False

        return True

    def as_tuple(self) -> tuple:
        """
        Returns dataclass instance represented as a tuple.
        """
        return self.discord_user_id, self.osu_user_id, self.osu_game_mode
