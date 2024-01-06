from discord.ext import commands
from discord.ext.commands import Context

from factories import UtilsFactory


async def check_is_config_set_up(ctx: Context) -> bool:
    """
    Checks If discord user set up the config.
    """
    db_manager = UtilsFactory.get_db_manager()
    user_info = await db_manager.users.get_user_info(ctx.author.id)
    if not user_info:
        raise commands.CheckFailure("Sorry, but you must set up the config first (config_change)")

    return True


async def check_is_user_has_scores(ctx: Context) -> bool:
    """
    Checks If discord user has at least one score in 'scores' table.
    """
    db_manager = UtilsFactory.get_db_manager()
    user_info = await db_manager.users.get_user_info(ctx.author.id)
    has_scores = await db_manager.scores.check_if_user_has_scores(user_info)
    if not has_scores:
        raise commands.CheckFailure("Sorry, but you have no scores (load_all_user_scores)")

    return True


async def check_is_user_has_beatmaps(ctx: Context) -> bool:
    """
    Checks If discord user has at least one beatmap in 'user_played_beatmaps' table.
    """
    db_manager = UtilsFactory.get_db_manager()
    user_info = await db_manager.users.get_user_info(ctx.author.id)
    has_beatmaps = await db_manager.user_played_beatmaps.check_if_user_has_beatmaps(user_info)
    if not has_beatmaps:
        raise commands.CheckFailure("Sorry, but you have no scores (load_all_user_played_beatmaps)")

    return True
