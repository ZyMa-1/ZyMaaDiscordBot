import asyncio
from typing import List

from discord.ext import commands
from discord.ext.commands import Context

from core import BotContext
import discord_extension_stuff.predicates.permission_predicates as predicates
from db_managers.data_classes import DbScoreInfo
from discord_extension_stuff.extras import Extras
from factories import UtilsFactory


class ScoresStatsCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.db_manager = UtilsFactory.get_db_manager()
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.extras = Extras(bot_context)

    @commands.command(name='load_all_user_scores')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def load_all_user_scores_command(self, ctx: Context):
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.osu_api_utils.get_all_user_beatmap_ids(user_info))
        is_task_completed = await self.extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                      timeout_sec=3600)
        if is_task_completed:
            beatmap_ids: List[int] = calc_task.result()
            for beatmap_id in beatmap_ids:
                score = await self.osu_api_utils.get_beatmap_user_best_score(beatmap_id, user_info)
                if score:
                    db_score_info = DbScoreInfo.from_score_and_user_info(score, user_info)
                    await self.db_manager.scores_table_manager.insert_score(db_score_info)
            await ctx.reply(f"Inserted {len(beatmap_ids)} scores into db")

    @commands.command(name='delete_all_user_scores')
    @commands.check(predicates.check_is_trusted and
                    predicates.check_is_config_set_up and
                    predicates.check_is_user_has_scores)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def delete_all_user_scores_command(self, ctx: Context):
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.db_manager.scores_table_manager.delete_all_user_scores(user_info))
        is_task_completed = await self.extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                      timeout_sec=3600)
        if is_task_completed:
            res: bool = calc_task.result()
            await ctx.reply(f"Deleted: {str(res)}")

    @commands.command(name='count_scores')
    @commands.check(predicates.check_is_trusted and
                    predicates.check_is_config_set_up and
                    predicates.check_is_user_has_scores)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def count_scores_command(self, ctx: Context):
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.db_manager.scores_table_manager.count_all_user_scores(user_info))
        is_task_completed = await self.extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                      timeout_sec=3600)

        if is_task_completed:
            scores_count: int = calc_task.result()
            await ctx.reply(f"Found {scores_count} scores")
