from discord.ext import commands
from discord.ext.commands import Context

from factories import UtilsFactory
from data_managers import DataUtils


async def check_is_trusted(ctx: Context) -> bool:
    """
    Checks If discord user is in 'trusted_users' list.
    """
    trusted_users = await DataUtils.load_trusted_users()
    if ctx.author.id not in trusted_users:
        raise commands.CheckFailure("Sorry, but you must have the `trusted user` permission to use this command")

    return True


async def check_is_admin(ctx: Context) -> bool:
    """
    Checks If discord user is in 'admins' list.
    """
    admins = await DataUtils.load_admin_users()
    if ctx.author.id not in admins:
        raise commands.CheckFailure(f"Sorry, but you must have the `admin` permission to use this command")

    return True


async def check_is_config_set_up(ctx: Context) -> bool:
    """
    Checks If discord user set up the config.
    """
    db_manager = UtilsFactory.get_db_manager()
    user_info = await db_manager.users_table_manager.get_user_info(ctx.author.id)
    if not user_info.is_config_set_up():
        raise commands.CheckFailure("Sorry, but you must set up the config (config_change)")

    return True


async def check_is_user_has_scores(ctx: Context) -> bool:
    """
    Checks If discord user has at least one score in 'scores' table.
    """
    db_manager = UtilsFactory.get_db_manager()
    user_info = await db_manager.users_table_manager.get_user_info(ctx.author.id)
    has_scores = await db_manager.scores_table_manager.check_if_user_has_scores(user_info)
    if not has_scores:
        raise commands.CheckFailure("Sorry, but you have no scores (load_all_user_scores)")

    return True
