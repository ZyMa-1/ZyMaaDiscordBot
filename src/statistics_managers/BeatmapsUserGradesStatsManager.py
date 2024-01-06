import io
from pprint import pformat
from typing import Dict, List, Any, Tuple

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from ossapi.enums import Grade

from core import PathManager
from db_managers.data_classes import DbUserInfo
from factories import UtilsFactory


class BeatmapsUserGradesStatsManager:
    """
    Class designed to easily calculate user's grade statistics on certain group of beatmaps.
    """

    def __init__(self, beatmap_ids: List[int], user_info: DbUserInfo, *, query_dict: dict):
        self.beatmap_ids = beatmap_ids
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.user_info = user_info
        self.query_dict = query_dict
        self.query_str = pformat(self.query_dict)

        self.beatmap_count: int = 0
        self.percent_completion: float = 0
        self.is_calculated = False
        self.plt_text: List[str] = []
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
        """
        Calculates user's grades, fills in statistic variables.
        Expected to be done only once.
        """
        if self.is_calculated:
            raise RuntimeError(f"Class instance cannot call {__name__} more than once")

        self.is_calculated = True
        for beatmap_id in self.beatmap_ids:
            grade = await self.osu_api_utils.get_user_beatmap_score_grade(beatmap_id, self.user_info)
            self.grades[grade] += 1
            self.beatmap_count += 1
        if self.beatmap_count != 0:
            self.percent_completion = round((1 - self.grades[None] / self.beatmap_count) * 100, 2)

        self.plt_text.append(f"User: {await self.user_info.osu_user_name()}")
        self.plt_text.append(f"Query: {self.query_str}")
        self.plt_text.append(f"Beatmaps: {self.beatmap_count}")
        self.plt_text.append(f"Completion: {self.beatmap_count - self.grades.get(None)}/{self.beatmap_count}, "
                             f"{self.percent_completion:.2f}%")

    def get_pretty_stats(self) -> str:
        """
        Returns a pretty stats string.
        """
        # max_grade_length = max(len(str(value)) for value in self.grades.values())
        return '\n'.join(self.plt_text)

    async def get_bar_plot(self) -> io.BytesIO:
        """
        Builds bar plot using 'matplotlib'.
        Returns plot image bytes.
        """
        grades = []
        values = []
        colors = []
        for key, value in self.grades.items():
            if key is not None:
                grades.append(str(key.value))
                values.append(value)
                colors.append(self.grade_colors[key])

        plt.figure(figsize=(8, 6))
        plt.bar(grades, values, width=0.6, color=colors)

        # Add notes
        plt.text(0.1, 0.05, self.get_pretty_stats(), transform=plt.gcf().transFigure)

        # Adjust bottom space
        plt.subplots_adjust(bottom=0.05 * self.get_pretty_stats().count('\n') + 0.05)

        plt.xlabel("Grades")
        plt.ylabel("Count")
        plt.title("Grade Distribution")

        # Set the vertical axis to show only integer values
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

        # Annotate the max value with an arrow and 'max' text
        max_value = max(values)
        max_index = values.index(max_value)
        offset = 5  # Adjust the offset to control the distance of the arrow and text
        plt.annotate(
            'Max',
            xy=(max_index, max_value),
            xytext=(0, offset),
            textcoords='offset points',
            ha='center',
            va='bottom',
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3'),
            fontsize=8,
        )

        plot_bytes = io.BytesIO()
        plt.savefig(plot_bytes, format="png")
        plot_bytes.seek(0)

        plt.close()

        return plot_bytes

    async def get_pie_plot(self) -> io.BytesIO:
        """
        Builds pie plot using 'matplotlib'.
        Returns plot image bytes.
        """
        grades = []
        values = []
        colors = []
        for key, value in self.grades.items():
            if key is not None:
                grades.append(str(key.value))
                values.append(value)
                colors.append(self.grade_colors[key])

        # Create figure and axes with space for the image
        fig, ax = plt.subplots(figsize=(8, 6))  # Adjust figsize as needed

        # Create a placeholder for the image
        imagebox = fig.add_axes([0.8, 0.6, 0.4, 0.25])  # Position and size of the image
        imagebox.axis('off')  # Turn off axes

        # Add the image to the placeholder using matplotlib's imread
        image = plt.imread(PathManager.random_anime_girl())
        imagebox.imshow(image)

        # Adjust spacing for title
        plt.subplots_adjust(top=0.9)  # Increase space at the top

        # Add plot title (adjust y position as needed)
        plt.suptitle("Grade Distribution", fontsize=12, y=0.92)  # Use suptitle to place above only the axes

        # Create the pie chart within the axes
        ax.pie(values, labels=None, colors=colors, startangle=90, autopct='')

        # Add notes
        plt.text(0.3, 0.20, self.get_pretty_stats(), transform=plt.gcf().transFigure)

        # Adjust bottom space
        plt.subplots_adjust(bottom=0.05 * self.get_pretty_stats().count('\n') + 0.05)

        # Adjust legend position
        legend_entries = [f"{grade}: {value}" for grade, value, color in zip(grades, values, colors)]
        ax.legend(legend_entries, title="Grades", loc="upper left",
                  bbox_to_anchor=(1.05, 1))  # Adjust anchor to avoid image

        # Finalize and save the plot
        plot_bytes = io.BytesIO()
        plt.savefig(plot_bytes, format="png", bbox_inches='tight')
        plot_bytes.seek(0)
        plt.close()
        return plot_bytes

    async def get_all_plots(self) -> Tuple[Tuple[str, io.BytesIO], Tuple[str, io.BytesIO]]:
        return ("bar", await self.get_bar_plot()), ("pie", await self.get_pie_plot())

# f"""
# Silver SS - {self.grades[Grade.SSH]:>{max_grade_length}}
# Silver S  - {self.grades[Grade.SH]:>{max_grade_length}}
# Just SS   - {self.grades[Grade.SS]:>{max_grade_length}}
# Just S    - {self.grades[Grade.S]:>{max_grade_length}}
# A         - {self.grades[Grade.A]:>{max_grade_length}}
# B         - {self.grades[Grade.B]:>{max_grade_length}}
# C         - {self.grades[Grade.C]:>{max_grade_length}}
# D         - {self.grades[Grade.D]:>{max_grade_length}}
# No scores - {self.grades[None]:>{max_grade_length}}
# {'-' * 12}
# Total map count: {self.beatmap_count}
# {'-' * 12}
# So far {self.percent_completion}% completion!
# """
