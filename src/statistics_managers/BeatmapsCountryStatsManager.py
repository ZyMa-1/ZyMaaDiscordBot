from typing import List

from db_managers.data_classes.DbUserInfo import DbUserInfo
from factories import UtilsFactory


class BeatmapsCountryStatsManager:
    def __init__(self, beatmap_ids: List[int], user_info: DbUserInfo):
        self.beatmap_ids = beatmap_ids
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.user_info = user_info

