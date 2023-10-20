from discord.ext import commands
from discord.ext.commands import Context
import discord

import discord_extension_stuff.predicates.permission_predicates as predicates
from core import BotContext
from factories import UtilsFactory
from data_managers import DataUtils
from db_managers.data_classes.DbUserInfo import DbUserInfo
from discord_extension_stuff.extras import Extras


class LogicCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.api_utils = UtilsFactory.get_osu_api_utils()
        self.db_manager = UtilsFactory.get_discord_users_data_db_manager()
        self.extras = Extras(bot_context)

    @commands.command(name='config_change')
    @commands.check(predicates.check_is_trusted)
    async def config_change_command(self, ctx: Context, osu_user_id: int, osu_game_mode: str):
        user_info = DbUserInfo(ctx.author.id, osu_user_id, osu_game_mode)
        if not user_info.is_fields_valid():
            response = "Sorry, but specified fields are not valid"
        elif not self.api_utils.check_if_user_exists(user_info.osu_user_id):
            response = "Sorry, but osu user with specified id does not exist."
        else:
            await self.db_manager.insert_user_info(user_info)
            response = (f"Successfully changed `osu_user_id` to {user_info.osu_user_id} and `osu_game_mode` to "
                        f"{user_info.osu_game_mode}")
        await ctx.reply(response)

    @commands.command(name='config_check')
    @commands.check(predicates.check_is_trusted)
    async def config_check_command(self, ctx: Context):
        user_info = await self.db_manager.get_user_info(ctx.author.id)
        response = f"Your `{user_info.osu_user_id=}` and `{user_info.osu_game_mode=}`"
        await ctx.send(response)

    @commands.command(name='trusted_users')
    async def trusted_users_command(self, ctx: Context):
        response = f"Trusted users:\n{await DataUtils.load_trusted_users()}"
        await ctx.send(response)

    @commands.command(name='admins')
    async def admins_command(self, ctx: Context):
        response = f"Admin users:\n{await DataUtils.load_admin_users()}"
        await ctx.send(response)

    @commands.command(name='add_trusted_user')
    @commands.check(predicates.check_is_admin)
    async def add_trusted_user_command(self, ctx: Context, user: discord.Member):
        await DataUtils.add_trusted_user(user.id)
        response = f"User with id: {user.id} added to trusted users."
        await ctx.send(response)
        response = f"Trusted users:\n{await DataUtils.load_trusted_users()}"
        await ctx.send(response)

    @commands.command(name='remove_trusted_user')
    @commands.check(predicates.check_is_admin)
    async def remove_trusted_user_command(self, ctx: Context, user: discord.Member):
        await DataUtils.remove_trusted_user(user.id)
        response = f"User with id: {user.id} was removed from trusted users."
        await ctx.send(response)
        response = f"Trusted users:\n{await DataUtils.load_trusted_users()}"
        await ctx.send(response)
