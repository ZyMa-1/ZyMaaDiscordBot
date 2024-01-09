import asyncio
import time
from typing import List

from discord.ext.commands import Context
from ossapi import BeatmapCompact, Beatmap

from core import BotContext
from db_managers.data_classes import DbScoreInfo, DbUserInfo, DbUserPlayedBeatmapInfo
from factories import UtilsFactory
from statistics_managers import BeatmapsUserGradesStatsManager


class DbExtras:
    """
    Class designed to mix things up!
    """

    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.db_manager = UtilsFactory.get_db_manager()

    async def calculate_beatmapsets_grade_stats(self, query: str, user_info: DbUserInfo) \
            -> BeatmapsUserGradesStatsManager:
        """
        Calculates beatmapsets_stats by querying 'search_all_beatmapsets' method of 'OsuApiUtils'.
        Wraps it into the 'BeatmapsetsUserGradesStatisticManager' class at last.
        """
        combined_beatmapset_search_res = await self.osu_api_utils.search_all_beatmapsets(query,
                                                                                         mode=user_info.osu_game_mode)
        beatmap_ids: List[int] = []
        for beatmapset in combined_beatmapset_search_res.beatmapsets:
            for beatmap in beatmapset.beatmaps:
                beatmap_ids.append(beatmap.id)

        stats = BeatmapsUserGradesStatsManager(beatmap_ids, user_info,
                                               query_dict=self.osu_api_utils.get_last_search_query_dict())
        await stats.calculate_user_grades()
        return stats

    async def insert_best_scores_into_db(self, ctx: Context,
                                         beatmaps: List[BeatmapCompact | Beatmap | int | DbUserPlayedBeatmapInfo],
                                         user_info: DbUserInfo) -> int:
        """
        Obtains best scores of a user's on all given beatmaps and inserts them into database.
        """
        progress_msg = await ctx.reply("Calculating scores...\n"
                                       f"Remaining: ~{len(beatmaps)}")
        res: int = 0
        try:
            start_time = time.perf_counter()
            for ind, beatmap in enumerate(beatmaps):
                beatmap_id = None
                if isinstance(int, beatmap):
                    beatmap_id = beatmap
                elif isinstance((BeatmapCompact, Beatmap), beatmap):
                    beatmap_id = beatmap.id
                elif isinstance(DbUserPlayedBeatmapInfo, beatmap):
                    beatmap_id = beatmap.beatmap_id
                score = await self.osu_api_utils.get_beatmap_user_best_score(beatmap_id, user_info)
                if ind % 100 == 0:
                    await progress_msg.edit(content=f"Calculating scores...\n"
                                                    f"Remaining: ~{len(beatmaps) - ind}")

                if score:
                    score_info = DbScoreInfo.from_score_and_user_info(score, user_info)
                    res += await self.db_manager.scores.merge_score_info(score_info)
            end_time = time.perf_counter()
            await ctx.reply(f"Done in {end_time - start_time:.6f} seconds")
        except asyncio.CancelledError:
            pass
        return res
