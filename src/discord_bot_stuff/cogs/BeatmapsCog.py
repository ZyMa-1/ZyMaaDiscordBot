import asyncio

from discord.ext import commands
from discord.ext.commands import Context

from core import BotContext
from db_managers.data_classes import DbUserPlayedBeatmapInfo
from discord_bot_stuff.extras import DbExtras, DiscordExtras
from discord_bot_stuff.predicates import combined_predicates
from factories import UtilsFactory


class BeatmapsCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.db_manager = UtilsFactory.get_db_manager()
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.db_extras = DbExtras(bot_context)
        self.discord_extras = DiscordExtras(bot_context)

    @commands.command(name='load_all_user_played_beatmaps')
    @commands.check(combined_predicates.trusted_and_config)
    @commands.cooldown(1, 60 * 60 * 2, commands.BucketType.user)
    async def load_all_user_played_beatmaps_command(self, ctx: Context):
        """
        Loads all user played beatmaps into the database table.
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.osu_api_utils.get_all_user_beatmaps(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60 * 2)
        if is_task_completed:
            beatmaps = calc_task.result()
            count = 0
            for beatmap in beatmaps:
                db_beatmap = DbUserPlayedBeatmapInfo.from_beatmap_and_user_info(beatmap, user_info)
                count += await self.db_manager.user_played_beatmaps.merge_user_beatmap(db_beatmap)
            await ctx.reply(f"Inserted `{count}` beatmaps into db")

    @commands.command(name='delete_all_user_beatmaps')
    @commands.check(combined_predicates.beatmaps_ready)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def delete_all_user_beatmaps_command(self, ctx: Context):
        """
        Deletes all user's beatmaps from the database table.
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        beatmap_count = await self.db_manager.user_played_beatmaps.count_all_user_beatmaps(user_info)
        calc_task = asyncio.create_task(self.db_manager.user_played_beatmaps.delete_all_user_beatmaps(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60)
        if is_task_completed:
            res: bool = calc_task.result()
            await ctx.reply(f"Deleted {str(res)} - `{beatmap_count}` beatmaps")

    @commands.command(name='count_beatmaps')
    @commands.check(combined_predicates.beatmaps_ready)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def count_beatmaps_command(self, ctx: Context):
        """
        Counts amount of user's beatmaps in the database table.
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.db_manager.user_played_beatmaps.count_all_user_beatmaps(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60)

        if is_task_completed:
            beatmaps_count: int = calc_task.result()
            await ctx.reply(f"Found `{beatmaps_count}` beatmaps")

    @commands.command(name='get_random_beatmap')
    @commands.check(combined_predicates.beatmaps_ready)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def get_random_beatmap_command(self, ctx: Context):
        """
        Gets user's random beatmap stored in the database table
        and responds with the data accosted about it.
        """
        user_info = await self.db_manager.users.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.db_manager.user_played_beatmaps.get_user_random_beatmap(user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60)

        if is_task_completed:
            beatmap_info: DbUserPlayedBeatmapInfo = calc_task.result()
            await ctx.reply(f"{DbUserPlayedBeatmapInfo.__name__} instance:\n{beatmap_info}")
