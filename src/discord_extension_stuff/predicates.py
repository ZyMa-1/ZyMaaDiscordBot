from discord.ext.commands import Context

from src.data_managers.data_utils import load_trusted_users, load_admin_users
from src.db_managers.discord_users_data_db_manager import DiscordUsersDataDbManager


async def check_is_trusted(ctx: Context) -> bool:
    trusted_users = await load_trusted_users()
    user_id = ctx.author.id
    print("predicate check is trusted", trusted_users, user_id)
    if user_id in trusted_users:
        return True
    else:
        await ctx.reply("Sorry, but you must have the permission to use this command")
        return False


async def check_is_config_set_up(ctx: Context) -> bool:
    db_manager: DiscordUsersDataDbManager = DiscordUsersDataDbManager()
    osu_user_id, osu_game_mode = await db_manager.get_user_info(ctx.author.name)
    print("predicate check is config set up", db_manager, osu_user_id, osu_game_mode)
    if osu_user_id is None or osu_game_mode is None:
        await ctx.reply("Sorry, but you must set up the config")
        return False

    return True


async def check_is_admin(ctx: Context) -> bool:
    admins = await load_admin_users()
    user_id = ctx.author.id
    print("predicate check is admin", admins, user_id)
    if user_id in admins:
        return True
    else:
        await ctx.reply("Sorry, but you must have the permission to use this command")
        return False
