import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context

import discord_extension_stuff.predicates.permission_predicates as predicates
from core import BotContext
from db_managers.data_classes import DbScoreInfo, DbUserPlayedBeatmapInfo
from discord_extension_stuff.converters import ModsConverter
from discord_extension_stuff.extras import DbExtras, DiscordExtras
from factories import UtilsFactory
from statistics_managers import ExcelScoresManager


class ScoresStatsCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.db_manager = UtilsFactory.get_db_manager()
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.db_extras = DbExtras(bot_context)
        self.discord_extras = DiscordExtras(bot_context)

    @commands.command(name='load_all_user_played_beatmaps')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    @commands.cooldown(1, 60 * 60 * 2, commands.BucketType.user)
    async def load_all_user_played_beatmaps_command(self, ctx: Context):
        """
        Loads all user played beatmaps into the database table.
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.osu_api_utils.get_all_user_beatmaps(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60 * 2)
        if is_task_completed:
            beatmaps = calc_task.result()
            for beatmap in beatmaps:
                db_beatmap = DbUserPlayedBeatmapInfo.from_beatmap_and_user_info(beatmap, user_info)
                await self.db_manager.user_played_beatmaps_table_manager.merge_user_played_beatmap(db_beatmap)
            await ctx.reply(f"Inserted `{len(beatmaps)}` beatmaps into db")

    @commands.command(name='load_all_user_scores')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    @commands.cooldown(1, 60 * 60 * 48, commands.BucketType.user)
    async def load_all_user_scores_command(self, ctx: Context):
        """
        Loads all scores to the database table according to 'user_played_beatmaps' database table.

        For example the user ever played 10000 maps.
        It would take about 10100 requests to the api.
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        beatmaps = await self.db_manager.user_played_beatmaps_table_manager.get_all_user_beatmaps(user_info)
        calc_task = asyncio.create_task(self.db_extras.insert_best_scores_into_db(ctx, beatmaps, user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60 * 48)
        if is_task_completed:
            await ctx.reply(f"Inserted `{len(beatmaps)}` scores into db")

    @commands.command(name='delete_all_user_scores')
    @commands.check(predicates.check_is_trusted and
                    predicates.check_is_config_set_up and
                    predicates.check_is_user_has_scores)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def delete_all_user_scores_command(self, ctx: Context):
        """
        Deletes all user's scores from the database table.
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        score_count = await self.db_manager.scores_table_manager.count_all_user_scores(user_info)
        calc_task = asyncio.create_task(self.db_manager.scores_table_manager.delete_all_user_scores(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60)
        if is_task_completed:
            res: bool = calc_task.result()
            await ctx.reply(f"Deleted {str(res)} - `{score_count}` scores")

    @commands.command(name='count_scores')
    @commands.check(predicates.check_is_trusted and
                    predicates.check_is_config_set_up and
                    predicates.check_is_user_has_scores)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def count_scores_command(self, ctx: Context):
        """
        Counts amount of user's scores in the database table.
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.db_manager.scores_table_manager.count_all_user_scores(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60)

        if is_task_completed:
            scores_count: int = calc_task.result()
            await ctx.reply(f"Found `{scores_count}` scores")

    @commands.command(name='get_random_score')
    @commands.check(predicates.check_is_trusted and
                    predicates.check_is_config_set_up and
                    predicates.check_is_user_has_scores)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def get_random_score_command(self, ctx: Context):
        """
        Gets user's random score stored in the database table
        and responds with the data accosted about it.
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.db_manager.scores_table_manager.get_user_random_score(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60)

        if is_task_completed:
            score_info: DbScoreInfo = calc_task.result()
            score: dict = score_info.deserialize_score_json()
            # await ctx.reply(f"Score deserialized into dictionary successfully. Here is `{score['id']=}` as a prove.")
            await ctx.reply(f"{DbScoreInfo.__name__} instance:\n{score_info}")

    @commands.command(name='get_xlsx_scores_file')
    @commands.check(predicates.check_is_trusted and
                    predicates.check_is_config_set_up and
                    predicates.check_is_user_has_scores)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def get_xlsx_scores_file_command(self, ctx: Context):
        """
        Gets xlsx file of all user's scores.
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        excel_scores_manager = ExcelScoresManager(user_info,
                                                  await self.db_manager.scores_table_manager.
                                                  get_all_user_scores(user_info))
        await excel_scores_manager.retrieve_rows()
        file_path = excel_scores_manager.save_workbook()
        file = discord.File(fp=file_path, filename=f"scores_{user_info.osu_user_id}"
                                                   f"{excel_scores_manager.file_extension}")
        await ctx.reply(file=file)
        excel_scores_manager.delete_temp_file()

    @commands.command(name='get_filtered_by_mods_xlsx_scores_file')
    @commands.check(predicates.check_is_trusted and
                    predicates.check_is_config_set_up and
                    predicates.check_is_user_has_scores)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def get_xlsx_scores_file_filtered_mods_command(self, ctx: Context, mods: ModsConverter):
        """
        Gets xlsx file of all user's scores that include specific mods (game modifications).
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        excel_scores_manager = ExcelScoresManager(user_info,
                                                  await self.db_manager.scores_table_manager.
                                                  get_mods_filtered_user_scores(user_info, mods))
        await excel_scores_manager.retrieve_rows()
        file_path = excel_scores_manager.save_workbook()
        file = discord.File(fp=file_path, filename=f"scores_{user_info.osu_user_id}_filtered_{mods.short_name}"
                                                   f"{excel_scores_manager.file_extension}")
        await ctx.reply(file=file)
        excel_scores_manager.delete_temp_file()
