import asyncio
from asyncio import Task
from typing import List

import discord
from discord import Message
from discord.ext.commands import Context

from core import BotContext
from db_managers.data_classes import DbScoreInfo, DbUserInfo
from factories import UtilsFactory
from statistics_managers import BeatmapsUserGradesStatsManager


class Extras:
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

        stats = BeatmapsUserGradesStatsManager(beatmap_ids, user_info)
        await stats.calculate_user_grades()
        return stats

    async def insert_best_scores_into_db(self, ctx: Context, beatmap_ids: List[int], user_info: DbUserInfo):
        """
        Obtains best scores of a user's on all given beatmaps and inserts them into database.
        """
        progress_msg = await ctx.reply("Calculating scores...\n"
                                       f"Remaining: {len(beatmap_ids)}")
        try:
            for ind, beatmap_id in enumerate(beatmap_ids):
                score = await self.osu_api_utils.get_beatmap_user_best_score(beatmap_id, user_info)
                if ind % 100 == 0:
                    await progress_msg.edit(content=f"Calculating scores...\n"
                                                    f"Remaining: ~{len(beatmap_ids) - ind}")

                if score:
                    score_info = DbScoreInfo.from_score_and_user_info(score, user_info)
                    await self.db_manager.scores_table_manager.insert_score(score_info)
        except asyncio.CancelledError:
            pass
        finally:
            ...
            # await asyncio.sleep(.5)
            # await progress_msg.delete()

    async def wait_for_reply(self, ctx: Context, start_msg: Message, *, reply_message_content: str,
                             timeout: int) -> bool:
        """
        Waits for the reply on certain message.
        Returns True if reply happened, False if not.
        """

        def check_reply(msg: Message):
            return (
                    msg.author == ctx.author
                    and msg.channel == ctx.channel
                    and msg.reference.message_id == start_msg.id
                    and msg.content.lower() == reply_message_content
            )

        try:
            await self.bot.wait_for("message", check=check_reply, timeout=timeout)

        except asyncio.TimeoutError:
            return False

        except asyncio.CancelledError:
            return False

        return True

    async def format_discord_id_list(self, discord_user_ids: List[int]) -> str:
        """
        Adds extra info to the 'discord_user_id_list' and returns ready to be printed string.
        Used for 'trusted_users' and 'admins' commands.
        """
        user_info_list = []

        for user_id in discord_user_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                user_info = (user.id, user.name)
                user_info_list.append(user_info)

            except discord.NotFound:
                user_info_list.append((user_id, "User not found"))

            except discord.HTTPException:
                user_info_list.append((user_id, "Error fetching user"))

        user_info_formatted = '\n'.join([str(item) for item in user_info_list])
        return user_info_formatted

    async def wait_till_task_complete(self, ctx: Context, *, calc_task: Task, timeout_sec: int = 3600) -> bool:
        """
        Creates a task that can be terminated by a discord user.
        Handles interaction between discord user and bot.
        Returns True If the task was completed, False otherwise.

        Further scaling of 'wait_for_reply'.
        """
        start_msg = await ctx.reply("Calculating... (reply stop to stop)")
        wait_for_reply_task = asyncio.create_task(
            self.wait_for_reply(ctx, start_msg, reply_message_content='stop', timeout=timeout_sec))
        done, pending = await asyncio.wait([calc_task, wait_for_reply_task], return_when=asyncio.FIRST_COMPLETED)

        await start_msg.delete()

        for task in pending:
            task.cancel()

        if calc_task in done:
            return True
        else:
            response = "Calculation canceled"
            await ctx.reply(response)
            return False
