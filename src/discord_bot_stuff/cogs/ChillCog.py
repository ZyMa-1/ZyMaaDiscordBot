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
        Describes the flow of the bot and the process to access certain commands.
        """
        response = ("Proceed directly to the following steps:\n"
                    "Consider using the `^get_filtered_by_mods_xlsx_scores_file` command.\n"
                    "\n"
                    "Begin by obtaining 'trusted_user' status.\n"
                    "Submit your application to the primary administrator using the\n"
                    "`^send_trusted_user_application` command.\n"
                    "\n"
                    "Await approval or denial from the administrator.\n"
                    "Configure your osu! settings.\n"
                    "Utilize the `^config_change` command to modify the configuration.\n"
                    "For instance, if your osu! user id is `16357858` and you play `osu` (std) game mode,\n"
                    "execute the command `^config_change 16357858 osu` to set up your config.\n"
                    "\n"
                    "Commands like `^beatmapsets_stats` and `^beatmap_playcount_slow` are now accessible.\n"
                    "\n"
                    "Load all beatmaps user has ever played into the bot's database using\n"
                    "`^load_all_user_played_beatmaps`.\n"
                    "Load all scores into the bot's database with `^load_all_user_scores`.\n"
                    "This process may take a considerable amount of time.\n"
                    "For instance, processing 11000 scores took almost a day.\n"
                    "You can erase all scores from the database using `^delete_all_user_scores`\n"
                    "to recalculate or simply delete them.\n"
                    "\n"
                    "Now you are ready to utilize the\n"
                    "`^get_xlsx_scores_file` and `^get_filtered_by_mods_xlsx_scores_file` commands.\n"
                    "The output will be a '.xlsx' file.\n"
                    "Feel free to use it in any way you prefer.\n"
                    "\n"
                    "This concludes the operational flow of the bot!")
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

    @commands.command(name="sing_glory_days")
    async def sing_random_song_command(self, ctx: Context):
        content = "Singing Glory Days:\n"
        message = await ctx.send(content)

        lyrics = (
            "♫To seek the glory days♫",
            "♫We'll fight the lion's way♫",
            "♫Then let the rain wash♫",
            "♫All of our pride away♫",
            "♫So if this victory♫",
            "♫Is our last odyssey♫",
            "♫Then let the power within us decide!♫"
        )
        sleep_times = (
            2.4,
            2.63,
            2.68,
            2.72,
            2.76,
            2.73,
            0
        )
        avg_delay = 0.35

        for line, sleep_time in zip(lyrics, sleep_times):
            content += "\n" + line
            await message.edit(content=content)
            await asyncio.sleep(sleep_time - avg_delay)
