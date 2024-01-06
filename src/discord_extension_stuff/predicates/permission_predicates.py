from discord.ext import commands
from discord.ext.commands import Context

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
