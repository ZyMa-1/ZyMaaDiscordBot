import asyncio

import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Context
from ossapi import GameMode

import initialize_project
from src.api_utils.ApiUtils import ApiUtils
from src.data_managers import data_utils
from src.db_managers.discord_users_data_db_manager import DiscordUsersDataDbManager
from src.statistics_managers.BeatmapsetsStatisticManager import BeatmapsetsUserStatisticManager

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='^', intents=intents)
bot.remove_command('help')  # Removing builtin help command

api_utils: ApiUtils | None = None
db_manager: DiscordUsersDataDbManager | None = None


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_guild_join(guild):
    # Respond when first entered a server.
    welcome_message = f"Hellow! I am a mini discord bot which can be used to" \
                      f"get some user statistic on a certain group of beatmaps by searching them." \
                      f"You can use `/config` to configure your `user_id` and `game mode`."
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(welcome_message)
            break


@bot.command(name='test')
async def test_command(ctx: Context):
    response = "test"
    await ctx.send(response)


@bot.command(name='help')
async def help_command(ctx: Context):
    response = """
```
List of commands:
^test - Test

^help - Get some help

^(пиво, пива, пивасик, пивасика, beer){cnt: int = 1} - The bot will serve you beer emoji

^config_change{osu_used_id: int}{osu_game_mode: str - [osu, catch, mania, taiko]) - Change your config

^config_check - Check your config

^trusted_users - List of users who can use some data operating commands

^get_beatmap_group_grade_stats{query: int} - Get your grade stats on a certain group of beatmapsets, 
which is obtained by search query like in: https://osu.ppy.sh/beatmapsets
```
"""
    await ctx.reply(response)


@bot.command(aliases=['пиво', 'пива', 'пивасик', 'пивасика', 'beer'])
async def beer_command(ctx: Context, cnt: int = 1):
    response = "Вот ваше пиво месье: " + "🍺" * cnt
    await ctx.reply(response)


@bot.command(name='config_change')
async def config_change_command(ctx: Context, osu_user_id: int, osu_game_mode: str):
    if ctx.author.name not in await data_utils.load_trusted_users():
        response = "Sorry, but you must have permission to use this command"
    else:
        if osu_game_mode not in [mode.value for mode in GameMode]:
            response = "Sorry, but specified game mode is not valid."
        elif not api_utils.check_if_user_exists(osu_user_id):
            response = "Sorry, but user with specified id does not exist."
        else:
            await db_manager.insert_user_info(ctx.author.name, osu_user_id, osu_game_mode)
            response = f"Successfully changed `osu_user_id` to {osu_user_id} and `osu_game_mode` to {osu_game_mode}"
    await ctx.reply(response)


@bot.command(name='config_check')
async def config_check_command(ctx: Context):
    if ctx.author.name not in await data_utils.load_trusted_users():
        response = "Sorry, but you must have permission to use this command"
    else:
        osu_user_id, osu_game_mode = await db_manager.get_user_info_by_discord_username(ctx.author.name)
        response = f"Your `{osu_user_id=}` and `{osu_game_mode=}`"
    await ctx.send(response)


@bot.command(name='trusted_users')
async def trusted_users_command(ctx: Context):
    response = f"Trusted users:\n{', '.join(await data_utils.load_trusted_users())}"
    await ctx.send(response)


async def calculate_beatmap_stats(query: str, osu_user_id: int, osu_game_mode: str):
    combined_beatmapset_search_res = api_utils.search_all_beatmapsets(query, mode=osu_game_mode)
    beatmapsets_stats = BeatmapsetsUserStatisticManager(combined_beatmapset_search_res.beatmapsets,
                                                        osu_user_id,
                                                        osu_game_mode)
    await beatmapsets_stats.calculate_user_grades_background()
    return beatmapsets_stats


async def wait_for_stop_reply(ctx: Context, start_msg: Message, *, timeout: int):
    def check_reply(reply_message: Message):
        return (
                reply_message.author == ctx.author
                and reply_message.channel == ctx.channel
                and reply_message.reference.message_id == start_msg.id
        )

    try:
        reply_msg = await bot.wait_for("message", check=check_reply, timeout=timeout)
        # If the user replied with ^stop, cancel the command
        if reply_msg.content == "^stop":
            return True  # Command was cancelled

    except asyncio.TimeoutError:
        pass  # No ^stop reply within the timeout

    return False  # Command was not cancelled


@bot.command(name='get_beatmap_group_grade_stats')
async def get_beatmap_group_stats_command(ctx: Context, query: str):
    if ctx.author.name not in await data_utils.load_trusted_users():
        response = "Sorry, but you must have permission to use this command"
    else:
        osu_user_id, osu_game_mode = await db_manager.get_user_info(ctx.author.name)
        if osu_user_id is None or osu_game_mode is None:
            response = "Sorry, but you must set up the config"
        else:
            start_msg = await ctx.send("Calculating...")
            task1 = asyncio.create_task(calculate_beatmap_stats(query, osu_user_id, osu_game_mode))
            task2 = asyncio.create_task(wait_for_stop_reply(ctx, start_msg, timeout=3600))
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


async def run_bot():
    global api_utils, db_manager
    api_utils, db_manager = await initialize_project.initialize_resources()
    await db_manager.create_users_table()
    await bot.start(data_utils.load_discord_bot_token())


if __name__ == "__main__":
    asyncio.run(run_bot())

# TODO:
#  Connect git to a server.
