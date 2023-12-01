from discord.ext import commands
from discord.ext.commands import Context

from core import BotContext


class FunCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot

    @commands.command(name='about')
    async def beer_command(self, ctx: Context):
        """
        About the bot.
        """
        response = ("I made this bot to play with a bunch of osu! api v2 statistics.\n"
                    "The bot uses 'guest' osu! api v2 authorization grant.\n"
                    "That means some fancy statistics is unavailable :("
                    "Despite that, hope you will enjoy using it!")
        await ctx.send(response)

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
        Gives user a beer (on russian).

        Parameters:
        - cnt (int): Number of beers.
        """
        response = "Вот ваше пиво месье: " + "🍺" * cnt
        await ctx.send(response)
