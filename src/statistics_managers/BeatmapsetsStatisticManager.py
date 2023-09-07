import asyncio
from typing import Dict, List, Any

from ossapi import Beatmapset
from ossapi.enums import Grade

from src.api_utils.ApiUtilsFactory import ApiUtilsFactory


class BeatmapsetsUserStatisticManager:
    def __init__(self, beatmapsets: List[Beatmapset], user_id: int, game_mode: str):
        self.beatmapsets = beatmapsets
        self.api_utils = ApiUtilsFactory.get_api_instance()
        self.user_id = user_id
        self.game_mode = game_mode
        self.beatmap_count = 0
        self.grades: Dict[Any, int] = {
            Grade.SSH: 0,
            Grade.SH: 0,
            Grade.SS: 0,
            Grade.S: 0,
            Grade.A: 0,
            Grade.B: 0,
            Grade.C: 0,
            Grade.D: 0,
            None: 0
        }

    async def _calc_user_grades(self):
        for beatmapset in self.beatmapsets:
            for beatmap in beatmapset.beatmaps:
                grade = await asyncio.to_thread(self.api_utils.get_user_beatmap_score_grade,
                                                beatmap.id,
                                                self.user_id,
                                                self.game_mode)
                self.grades[grade] += 1
            self.beatmap_count += len(beatmapset.beatmaps)

    async def calculate_user_grades_background(self):
        await self._calc_user_grades()

    def get_pretty_stats(self):
        return f"""Silver SS - {self.grades[Grade.SSH]:<10}
Silver S  - {self.grades[Grade.SH]:<10}
Just SS   - {self.grades[Grade.SS]:<10}
Just S    - {self.grades[Grade.S]:<10}
A         - {self.grades[Grade.A]:<10}
B         - {self.grades[Grade.B]:<10}
C         - {self.grades[Grade.C]:<10}
D(ick)    - {self.grades[Grade.D]:<10}
No scores - {self.grades[None]:<10}
----------------------------------
Total map count: {self.beatmap_count}
"""
