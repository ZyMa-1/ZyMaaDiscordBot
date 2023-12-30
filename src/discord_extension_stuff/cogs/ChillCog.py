import asyncio

from discord.ext import commands
from discord.ext.commands import Context

from core import BotContext


class ChillCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot

    @commands.command(name='flow')
    async def flow_command(self, ctx: Context):
        """
        Describes the flow of the bot and how to get access to some commands.
        """
        response = ("Lets get straight to the point.\n"
                    "Assume you want to use the fancy `^get_filtered_by_mods_xlsx_scores_file` command.\n"
                    "\n"
                    "First you need to be the 'trusted_user'.\n"
                    "You can send the application to the first (main) admin using"
                    "`^send_trusted_user_application` command.\n"
                    "\n"
                    "Then the admin will accept or deny your request.\n"
                    "Next set up your osu! config.\n"
                    "Use `^config_change` command to change the config.\n"
                    "For example my osu! user id is `16357858` and I play `osu` (std) game mode.\n"
                    "So I will use `^config_change 16357858 osu` command to setup my config.\n"
                    "\n"
                    "Now commands like `^beatmapsets_stats` and `^beatmap_playcount_slow`\n"
                    "are already available for you.\n"
                    "\n"
                    "Next you can load all scores to the bot's database using `^load_all_user_scores` scores command.\n"
                    "It may take a long time, 11000 scores took almost one whole day.\n"
                    "You can delete all scores from the database using `^delete_all_user_scores` command\n"
                    "to recalculate all the scores again or to just delete them.\n"
                    "\n"
                    "Everything is prepared for the use of\n"
                    "`^get_xlsx_scores_file` and `^get_filtered_by_mods_xlsx_scores_file` commands.\n"
                    "The result of the commands will be '.xlsx file.\n"
                    "Use it however you want.\n"
                    "\n"
                    "That concludes the flow of the bot!")
        await ctx.send(response)

    @commands.command(name='about')
    async def about_command(self, ctx: Context):
        """
        About the bot.
        """
        response = ("I made this bot to play with a bunch of osu! api v2 statistics.\n"
                    "The bot uses 'guest' osu! api v2 authorization grant.\n"
                    "That means some fancy statistics is unavailable :(\n"
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
    async def beer_command(self, ctx: Context, cnt: int = 1):
        """
        Gives user a beer (on russian).

        Parameters:
        - cnt (int): Number of beers.
        """
        response = "Вот ваше пиво месье: " + "🍺" * cnt
        await ctx.send(response)

    @commands.command(name="sing_random_song")
    async def sing_random_song_command(self, ctx: Context):
        message = await ctx.send("Singing glory days:")

        lyrics = (
            "♫To seek the glory days♫",
            "♫We'll fight the lion's way♫",
            "♫Then let the rain wash♫",
            "♫All of our pride away♫"
            "♫So if this victory♫",
            "♫Is our last odyssey♫",
            "♫Then let the power within us decide!♫"
        )

        for line in lyrics:
            await asyncio.sleep(2.7)
            await message.edit(content=f"{message.content}\n{line}")
