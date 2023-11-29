from discord.ext.commands import Context

from factories import UtilsFactory
from data_managers import DataUtils


async def check_is_trusted(ctx: Context) -> bool:
    """
    Checks If discord user is in 'trusted_users' list.
    """
    trusted_users = await DataUtils.load_trusted_users()
    if ctx.author.id in trusted_users:
        return True
    else:
        await ctx.reply("Sorry, but you must have the `trusted user` permission to use this command")
        return False


async def check_is_admin(ctx: Context) -> bool:
    """
    Checks If discord user is in 'admins' list.
    """
    admins = await DataUtils.load_admin_users()
    if ctx.author.id in admins:
        return True
    else:
        await ctx.reply(f"Sorry, but you must have the `admin` permission to use this command")
        return False


async def check_is_config_set_up(ctx: Context) -> bool:
    """
    Checks If discord user set up the config.
    """
    db_manager = UtilsFactory.get_db_manager()
    user_info = await db_manager.users_table_manager.get_user_info(ctx.author.id)
    if not user_info.is_config_set_up():
        await ctx.reply("Sorry, but you must set up the config (config_change)")
        return False

    return True
