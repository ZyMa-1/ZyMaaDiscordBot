from typing import List

from db_managers.data_classes.DbUserInfo import DbUserInfo
from factories import UtilsFactory


class BeatmapsUserCountryStatsManager:
    def __init__(self, beatmap_ids: List[int], user_info: DbUserInfo):
        self.beatmap_ids = beatmap_ids
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.user_info = user_info

        self.is_calculated = False
        self.scores = []
        self.top_1_country_count: int = 0
        self.top_8_country_count: int = 0
        self.top_15_country_count: int = 0
        self.top_25_country_count: int = 0
        self.top_50_country_count: int = 0

    async def calculate_scores(self):
        """
        Calculates user's scores which are at least top 50 in the country's leaderboard.
        Expected to be done only once.
        """
        if self.is_calculated:
            raise RuntimeError(f"Class instance cannot call {__name__} more than once")

        self.is_calculated = True
        for beatmap_id in self.beatmap_ids:
            score = await self.osu_api_utils.get_user_country_top_x_score(beatmap_id, self.user_info, top_x=50)
            if score is not None:
                rank_country = score.rank_country
                self.scores.append(score)
                if rank_country <= 1:
                    self.top_1_country_count += 1
                if rank_country <= 8:
                    self.top_8_country_count += 1
                if rank_country <= 15:
                    self.top_15_country_count += 1
                if rank_country <= 25:
                    self.top_25_country_count += 1
                if rank_country <= 50:
                    self.top_50_country_count += 1

    def get_pretty_stats(self) -> str:
        """
        Returns pretty stats string.
        """
        return f"""In how many top X map country leaderboards are you?
Top 1   : {self.top_1_country_count:>6}
Top 8   : {self.top_8_country_count:>6}
Top 15  : {self.top_15_country_count:>6}
Top 25  : {self.top_25_country_count:>6}
Top 50  : {self.top_50_country_count:>6}
"""
