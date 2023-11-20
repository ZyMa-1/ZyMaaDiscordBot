import dataclasses
from dataclasses import dataclass
from typing import Optional

from ossapi import GameMode


@dataclass
class DbUserInfo:
    discord_user_id: int
    osu_user_id: Optional[int]
    osu_game_mode: Optional[str]

    def is_config_set_up(self) -> bool:
        if None in dataclasses.asdict(self).values():
            return False

        return True

    def are_fields_valid(self) -> bool:
        if self.osu_game_mode not in [mode.value for mode in GameMode]:
            return False

        return True

    def as_tuple(self) -> tuple:
        return self.discord_user_id, self.osu_user_id, self.osu_game_mode
