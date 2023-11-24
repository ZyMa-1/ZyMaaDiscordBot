from discord.ext import commands
from discord.ext.commands import Context

from core import BotContext


class FunCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot

    @commands.command(name='test')
    async def test_command(self, ctx: Context):
        """
        Test whether discord bot is working or not.
        """
        response = "test"
        await ctx.send(response)

    @commands.command(name='beer', aliases=['пиво', 'пива', 'пивасик', 'пивасика'])
    async def beer_command(self, ctx: Context, *, cnt: int = 1):
        """
        Gives user a beer.

        Parameters:
        - cnt (int): Number of beers.
        """
        response = "Вот ваше пиво месье: " + "🍺" * cnt
        await ctx.reply(response)
