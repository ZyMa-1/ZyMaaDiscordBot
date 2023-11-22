import io
from typing import Dict, List, Any

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from ossapi import Beatmapset
from ossapi.enums import Grade

from db_managers.data_classes.DbUserInfo import DbUserInfo
from factories import UtilsFactory


class BeatmapsetsUserStatisticManager:
    def __init__(self, beatmapsets: List[Beatmapset], user_info: DbUserInfo):
        self.beatmapsets = beatmapsets
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.user_info = user_info

        self.beatmap_count: int = 0
        self.percent_completion: float = 0
        self.is_calculated = False
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
        self.grade_colors: Dict[Any, str] = {
            Grade.SSH: "#EDEDED",
            Grade.SH: "#C0C0C0",
            Grade.SS: "#FFD800",
            Grade.S: "#FFA200",
            Grade.A: "#2CDB5D",
            Grade.B: "#1B2EE1",
            Grade.C: "#8B00ED",
            Grade.D: "#CD1C1C",
        }

    async def calculate_user_grades(self):
        if self.is_calculated:
            raise RuntimeError(f"Class instance cannot call {__name__} more than once")

        self.is_calculated = True
        for beatmapset in self.beatmapsets:
            for beatmap in beatmapset.beatmaps:
                grade = await self.osu_api_utils.get_user_beatmap_score_grade(beatmap.id, self.user_info)
                self.grades[grade] += 1
            self.beatmap_count += len(beatmapset.beatmaps)
        self.percent_completion = round((1 - self.grades[None] / self.beatmap_count) * 100, 2)

    def get_pretty_stats(self):
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
So far {self.percent_completion}% completion!
"""

    def get_bar_plot(self):
        grades = []
        values = []
        colors = []
        for key, value in self.grades.items():
            if key is not None:
                grades.append(str(key.value))
                values.append(value)
                colors.append(self.grade_colors[key])

        plt.figure(figsize=(8, 6))
        plt.subplots_adjust(bottom=0.2)
        plt.bar(grades, values, width=0.6, color=colors)

        # Add note on 'None' scores
        none_scores = self.grades.get(None, 0)
        plt.text(0.1, 0.075, f"*No scores: {none_scores}", transform=plt.gcf().transFigure)

        plt.xlabel("Grades")
        plt.ylabel("Count")
        plt.title("Grade Distribution")

        # Set the vertical axis to show only integer values
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

        plot_bytes = io.BytesIO()
        plt.savefig(plot_bytes, format="png")
        plot_bytes.seek(0)

        plt.close()

        return plot_bytes

    def get_pie_plot(self):
        grades = []
        values = []
        colors = []
        for key, value in self.grades.items():
            if key is not None:
                grades.append(str(key.value))
                values.append(value)
                colors.append(self.grade_colors[key])

        plt.figure(figsize=(8, 6))

        # Create pie chart without autopct
        plt.pie(values, labels=None, colors=colors, startangle=90, autopct='')

        # Add note on 'None' scores
        none_scores = self.grades.get(None, 0)
        plt.text(0.25, 0.15, f"*No scores: {none_scores}", transform=plt.gcf().transFigure)

        plt.title("Grade Distribution")

        # Add legend
        legend_entries = [f"{grade}: {value}" for grade, value, color in zip(grades, values, colors)]
        plt.legend(legend_entries, title="Grades", loc="center left", bbox_to_anchor=(1, 0.5))

        plot_bytes = io.BytesIO()
        plt.savefig(plot_bytes, format="png", bbox_inches='tight')
        plot_bytes.seek(0)

        plt.close()

        return plot_bytes
