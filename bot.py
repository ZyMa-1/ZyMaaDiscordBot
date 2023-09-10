import asyncio

import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Context
from ossapi import GameMode

import initialize_project
from src.api_utils.ApiUtils import ApiUtils
from src.api_utils.ApiUtilsFactory import ApiUtilsFactory
from src.data_managers import data_utils
from src.db_managers.discord_users_data_db_manager import DiscordUsersDataDbManager
from src.discord_extension_stuff import predicates
from src.discord_extension_stuff.MyHelpCommand import MyHelpCommand
from src.statistics_managers.BeatmapsetsStatisticManager import BeatmapsetsUserStatisticManager

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='^', intents=intents)
bot.help_command = MyHelpCommand()

api_utils: ApiUtils | None = None
db_manager: DiscordUsersDataDbManager | None = None


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_guild_join(guild):
    # Respond when first entered a server.
    welcome_message = f"Hellow! I am a mini discord bot made by .zymaa"
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(welcome_message)
            break


@bot.command(name='test')
async def test_command(ctx: Context):
    """
    Test whether discord bot working or not.
    """
    response = "test"
    await ctx.send(response)


@bot.command(aliases=['пиво', 'пива', 'пивасик', 'пивасика', 'beer'])
async def beer_command(ctx: Context, cnt: int = 1):
    """
    Gives user a beer.

    Parameters:
    - cnt (int): Number of the beers.
    """
    response = "Вот ваше пиво месье: " + "🍺" * cnt
    await ctx.reply(response)


@bot.command(name='config_change')
@commands.check(predicates.check_is_trusted)
async def config_change_command(ctx: Context, osu_user_id: int, osu_game_mode: str):
    """
    Change user's config.

    Parameters:
    - osu_user_id (int): Number of the beers.
    - osu_game_mode (str): ['osu', 'taiko', 'catch', 'mania'].
    """
    if osu_game_mode not in [mode.value for mode in GameMode]:
        response = "Sorry, but specified game mode is not valid."
    elif not api_utils.check_if_user_exists(osu_user_id):
        response = "Sorry, but user with specified id does not exist."
    else:
        await db_manager.insert_user_info(ctx.author.name, osu_user_id, osu_game_mode)
        response = f"Successfully changed `osu_user_id` to {osu_user_id} and `osu_game_mode` to {osu_game_mode}"
    await ctx.reply(response)


@bot.command(name='config_check')
@commands.check(predicates.check_is_trusted)
async def config_check_command(ctx: Context):
    """
    Prints out user's config values.
    """
    osu_user_id, osu_game_mode = await db_manager.get_user_info_by_discord_username(ctx.author.name)
    response = f"Your `{osu_user_id=}` and `{osu_game_mode=}`"
    await ctx.send(response)


@bot.command(name='trusted_users')
async def trusted_users_command(ctx: Context):
    """
    Prints out list of trusted users.
    """
    response = f"Trusted users:\n{await data_utils.load_trusted_users(populate=True)}"
    await ctx.send(response)


@bot.command(name='admins')
async def admins_command(ctx: Context):
    """
    Prints out list of admin users.
    """
    response = f"Admin users:\n{await data_utils.load_admin_users(populate=True)}"
    await ctx.send(response)


@bot.command(name='add_trusted_user')
@commands.check(predicates.check_is_admin)
async def add_trusted_user_command(ctx: Context, discord_user_id: int):
    """
    Adds trusted user by his Discord ID.
    """
    if await check_if_user_exists(ctx, discord_user_id):
        await data_utils.add_trusted_user(discord_user_id)
        response = f"User with id:{discord_user_id} added to trusted users."
        await ctx.send(response)
        response = f"Trusted users:\n{await data_utils.load_trusted_users(populate=True)}"
        await ctx.send(response)


@bot.command(name='remove_trusted_user')
@commands.check(predicates.check_is_admin)
async def remove_trusted_user_command(ctx: Context, discord_user_id: int):
    """
    Removes trusted user by his Discord ID.
    """
    if await check_if_user_exists(ctx, discord_user_id):
        await data_utils.remove_trusted_user(discord_user_id)
        response = f"User with id:{discord_user_id} was removed from trusted users."
        await ctx.send(response)
        response = f"Trusted users:\n{await data_utils.load_trusted_users(populate=True)}"
        await ctx.send(response)


@bot.command(name='beatmapsets_stats')
@commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
async def beatmapsets_stats_command(ctx: Context, query: str):
    """
    Get grade stats on certain group of beatmapsets.

    Parameters:
    - query (str)   : The search query. Can include filters like ranked<2019.
    - mode          : Mode from your config by default.
    """

    osu_user_id, osu_game_mode = await db_manager.get_user_info(ctx.author.name)
    start_msg = await \
        ctx.send("Calculating...")
    task1 = asyncio.create_task(calculate_beatmapsets_stats(query, osu_user_id, osu_game_mode))
    task2 = asyncio.create_task(wait_for_reply(ctx, start_msg, reply_message_content="^stop", timeout=3600))
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


async def check_if_user_exists(ctx: Context, discord_user_id: int) -> bool:
    """Checks if user with specified discord_id exists."""
    # Try to fetch the user by their ID
    user = bot.get_user(discord_user_id)

    if user is None:
        await ctx.reply(f"User with ID {discord_user_id} does not exist.")
        return False

    return True


async def calculate_beatmapsets_stats(query: str, osu_user_id: int, osu_game_mode: str):
    """Calculates beatmapsets_stats."""
    combined_beatmapset_search_res = api_utils.search_all_beatmapsets(query, mode=osu_game_mode)
    beatmapsets_stats = BeatmapsetsUserStatisticManager(combined_beatmapset_search_res.beatmapsets,
                                                        osu_user_id,
                                                        osu_game_mode)
    await beatmapsets_stats.calculate_user_grades_background()
    return beatmapsets_stats


async def wait_for_reply(ctx: Context, start_msg: Message, *, reply_message_content: str, timeout: int) -> bool:
    """Waits for the reply on certain message. Returns True if reply happened, False if not."""

    def check_reply(reply_message: Message):
        return (
                reply_message.author == ctx.author
                and reply_message.channel == ctx.channel
                and reply_message.reference.message_id == start_msg.id
        )

    try:
        reply_msg = await bot.wait_for("message", check=check_reply, timeout=timeout)
        # If the user replied with `reply_message_content`, cancel the command
        if reply_msg.content == reply_message_content:
            return True  # Command was cancelled

    except asyncio.TimeoutError:
        pass  # No ^stop reply within the timeout

    return False  # Command was not cancelled


async def run_bot():
    global api_utils, db_manager
    await initialize_project.initialize_resources()
    api_utils = ApiUtilsFactory.get_api_instance()
    db_manager = DiscordUsersDataDbManager()
    await db_manager.create_users_table()
    await bot.start(data_utils.load_discord_bot_token())


if __name__ == "__main__":
    asyncio.run(run_bot())
