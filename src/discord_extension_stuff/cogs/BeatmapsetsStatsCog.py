import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context

from core import BotContext
from discord_extension_stuff.extras import Extras
import discord_extension_stuff.predicates.permission_predicates as predicates
from factories import UtilsFactory
from statistics_managers import BeatmapsetsUserStatisticManager


class BeatmapsetsStatsCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.db_manager = UtilsFactory.get_discord_users_data_db_manager()
        self.extras = Extras(bot_context)

    @commands.command(name='beatmapsets_stats')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    async def beatmapsets_stats_command(self, ctx: Context, query: str):
        """
        Get grade stats on certain group of beatmapsets.

        Parameters:
        - query (str)   : The search query. Can include filters like ranked<2019.
        - mode          : Mode from your config by default.
        """
        user_info = await self.db_manager.get_user_info(ctx.author.id)
        start_msg = await \
            ctx.send("Calculating...")
        task1 = asyncio.create_task(self.extras.calculate_beatmapsets_stats(query, user_info))
        task2 = asyncio.create_task(
            self.extras.wait_for_reply(ctx, start_msg, reply_message_content="stop", timeout=3600))
        done, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)

        await start_msg.delete()

        for task in pending:
            task.cancel()

        for task in done:
            if task == task1:
                beatmapsets_stats: BeatmapsetsUserStatisticManager = task1.result()
                response = beatmapsets_stats.get_pretty_stats()
                await ctx.reply(response)
                image_bytes = beatmapsets_stats.get_grade_distribution_plot()
                image_file = discord.File(fp=image_bytes, filename=f"grade_distribution.png")
                await ctx.reply(file=image_file)

            else:
                response = "Command canceled"
                await ctx.reply(response)
