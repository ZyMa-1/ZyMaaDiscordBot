from discord.ext import commands
from discord.ext.commands import Context

from core import BotContext
from my_logging.LoggingStats import LoggingStats


class LoggingStatsCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.logging_stats = LoggingStats()

    @commands.command(name='logging_stats')
    async def logging_stats_command(self, ctx: Context):
        """
        Logging stats of osu! api v2 calls via 'ossapi' python wrapper.
        """
        response = await self.logging_stats.calculate_stats()
        await ctx.send(response)
