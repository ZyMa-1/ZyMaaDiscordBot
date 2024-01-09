import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context

from core import BotContext
from db_managers.data_classes import DbScoreInfo
from discord_extension_stuff.converters import ModsConverter
from discord_extension_stuff.extras import DbExtras, DiscordExtras
from discord_extension_stuff.predicates import combined_predicates
from factories import UtilsFactory
from statistics_managers import ExcelScoresManager


class ScoresCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.db_manager = UtilsFactory.get_db_manager()
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.db_extras = DbExtras(bot_context)
        self.discord_extras = DiscordExtras(bot_context)

    @commands.command(name='load_all_user_scores')
    @commands.check(combined_predicates.beatmaps_ready)
    @commands.cooldown(1, 60 * 60 * 48, commands.BucketType.user)
    async def load_all_user_scores_command(self, ctx: Context):
        """
        Loads all scores to the database table according to 'user_played_beatmaps' database table.

        For example the user ever played 10000 maps.
        It would take about 10100 requests to the api.
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        beatmaps = await self.db_manager.user_played_beatmaps.get_all_user_beatmaps(user_info)
        calc_task = asyncio.create_task(self.db_extras.insert_best_scores_into_db(ctx, beatmaps, user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60 * 48)
        if is_task_completed:
            res: int = calc_task.result()
            await ctx.reply(f"Inserted `{res}` scores into db")

    @commands.command(name='delete_all_user_scores')
    @commands.check(combined_predicates.scores_ready)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def delete_all_user_scores_command(self, ctx: Context):
        """
        Deletes all user's scores from the database table.
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        score_count = await self.db_manager.scores.count_all_user_scores(user_info)
        calc_task = asyncio.create_task(self.db_manager.scores.delete_all_user_scores(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60)
        if is_task_completed:
            res: bool = calc_task.result()
            await ctx.reply(f"Deleted {str(res)} - `{score_count}` scores")

    @commands.command(name='count_scores')
    @commands.check(combined_predicates.scores_ready)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def count_scores_command(self, ctx: Context):
        """
        Counts amount of user's scores in the database table.
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.db_manager.scores.count_all_user_scores(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60)

        if is_task_completed:
            scores_count: int = calc_task.result()
            await ctx.reply(f"Found `{scores_count}` scores")

    @commands.command(name='get_random_score')
    @commands.check(combined_predicates.scores_ready)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def get_random_score_command(self, ctx: Context):
        """
        Gets user's random score stored in the database table
        and responds with the data accosted about it.
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.db_manager.scores.get_user_random_score(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60)

        if is_task_completed:
            score_info: DbScoreInfo = calc_task.result()
            # score: dict = score_info.deserialize_score_json()
            # await ctx.reply(f"Score deserialized into dictionary successfully. Here is `{score['id']=}` as a prove.")
            await ctx.reply(f"{DbScoreInfo.__name__} instance:\n{score_info}")

    @commands.command(name='get_xlsx_scores_file')
    @commands.check(combined_predicates.scores_ready)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def get_xlsx_scores_file_command(self, ctx: Context):
        """
        Gets xlsx file of all user's scores.
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        excel_scores_manager = ExcelScoresManager(user_info,
                                                  await self.db_manager.scores.
                                                  get_all_user_scores(user_info))
        await excel_scores_manager.retrieve_rows()
        file_path = excel_scores_manager.save_workbook()
        file = discord.File(fp=file_path, filename=f"scores_{user_info.osu_user_id}"
                                                   f"{excel_scores_manager.file_extension}")
        await ctx.reply(file=file)
        excel_scores_manager.delete_temp_file()

    @commands.command(name='get_filtered_by_mods_xlsx_scores_file')
    @commands.check(combined_predicates.scores_ready)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def get_filtered_by_mods_xlsx_scores_file_command(self, ctx: Context, mods: ModsConverter):
        """
        Gets xlsx file of all user's scores that include specific mods (game modifications).
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        excel_scores_manager = ExcelScoresManager(user_info,
                                                  await self.db_manager.scores.
                                                  get_mods_filtered_user_scores(user_info, mods))
        await excel_scores_manager.retrieve_rows()
        file_path = excel_scores_manager.save_workbook()
        file = discord.File(fp=file_path, filename=f"scores_{user_info.osu_user_id}_filtered_{mods.short_name}"
                                                   f"{excel_scores_manager.file_extension}")
        await ctx.reply(file=file)
        excel_scores_manager.delete_temp_file()
