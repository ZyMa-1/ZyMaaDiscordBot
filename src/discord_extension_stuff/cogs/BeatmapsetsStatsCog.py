import asyncio

from discord.ext import commands
from discord.ext.commands import Context

from BotContext import BotContext
from src.db_managers.DiscordUsersDataDbManager import DiscordUsersDataDbManager
from src.discord_extension_stuff.extras import Extras
import src.discord_extension_stuff.predicates as predicates
from src.statistics_managers.BeatmapsetsStatisticManager import BeatmapsetsUserStatisticManager


class BeatmapsetsStatsCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.db_manager = DiscordUsersDataDbManager.get_instance()
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

        osu_user_id, osu_game_mode = await self.db_manager.get_user_info(ctx.author.name)
        start_msg = await \
            ctx.send("Calculating...")
        task1 = asyncio.create_task(self.extras.calculate_beatmapsets_stats(query, osu_user_id, osu_game_mode))
        task2 = asyncio.create_task(
            self.extras.wait_for_reply(ctx, start_msg, reply_message_content="^stop", timeout=3600))
        done, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()

        response = "Command canceled"
        for task in done:
            if task == task1:
                beatmapsets_stats: BeatmapsetsUserStatisticManager = task.result()
                response = beatmapsets_stats.get_pretty_stats()

        await start_msg.delete()
        await ctx.reply(response)
