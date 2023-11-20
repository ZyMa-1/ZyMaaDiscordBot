import asyncio
import io
from typing import Dict, List, Any

import matplotlib.pyplot as plt
from ossapi import Beatmapset
from ossapi.enums import Grade

from db_managers.data_classes.DbUserInfo import DbUserInfo
from factories import UtilsFactory


class BeatmapsetsUserStatisticManager:
    def __init__(self, beatmapsets: List[Beatmapset], user_info: DbUserInfo):
        self.beatmapsets = beatmapsets
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.user_info = user_info
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

    async def calculate_user_grades(self):
        for beatmapset in self.beatmapsets:
            for beatmap in beatmapset.beatmaps:
                grade = await self.osu_api_utils.get_user_beatmap_score_grade(beatmap.id, self.user_info)
                self.grades[grade] += 1
            self.beatmap_count += len(beatmapset.beatmaps)

    def get_pretty_stats(self):
        percent_completion = round((1 - self.grades[None] / self.beatmap_count) * 100, 2)
        return f"""Silver SS - {self.grades[Grade.SSH]:<10}
Silver S  - {self.grades[Grade.SH]:<10}
Just SS   - {self.grades[Grade.SS]:<10}
Just S    - {self.grades[Grade.S]:<10}
A         - {self.grades[Grade.A]:<10}
B         - {self.grades[Grade.B]:<10}
C         - {self.grades[Grade.C]:<10}
D         - {self.grades[Grade.D]:<10}
No scores - {self.grades[None]:<10}
----------------------------------
Total map count: {self.beatmap_count}
----------------------------------
So far {percent_completion}% completion!
"""

    def get_grade_distribution_plot(self):
        # MAKE A PIE PLOT INSTEAD DUDE
        grades = list([str(key.value) if isinstance(key, Grade) else str(key) for key in self.grades.keys()])
        values = list(self.grades.values())
        plt.figure(figsize=(8, 6))
        plt.bar(grades, values, width=0.6)

        plt.xlabel("Grades")
        plt.ylabel("Count")
        plt.title("Grade Distribution")

        plot_bytes = io.BytesIO()
        plt.savefig(plot_bytes, format="png")
        plot_bytes.seek(0)

        plt.close()

        return plot_bytes
