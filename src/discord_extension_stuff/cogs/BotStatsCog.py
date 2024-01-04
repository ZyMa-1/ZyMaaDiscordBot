import discord
from discord.ext import commands
from discord.ext.commands import Context

from discord_extension_stuff.cogs.ListenersCog import command_usage
from my_logging.LoggingStats import LoggingStats


class BotStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_stats = LoggingStats()

    @commands.command(name='logging_stats')
    async def logging_stats_command(self, ctx: Context):
        """
        Logging stats for 'OsuApiUtils' class (osu! api v2 calls via 'ossapi' python wrapper).
        """
        response = await self.logging_stats.calculate_stats()
        await ctx.reply(response)

    @commands.command(name='command_usage')
    async def command_usage_command(self, ctx: Context):
        """
        Display top 10 commands usage since the bot started.
        """
        sorted_commands = sorted(command_usage.items(), key=lambda x: x[1], reverse=True)
        top_commands = sorted_commands[:10]
        usage_data = '\n'.join(f'{command}: {count}' for command, count in top_commands)
        embed = discord.Embed(title="Top 10 Command Usage Statistics", description=usage_data, color=0x42f56c)
        await ctx.send(embed=embed)
