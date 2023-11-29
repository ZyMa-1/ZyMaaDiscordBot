from discord.ext import commands
from discord.ext.commands import Context
import discord

import discord_extension_stuff.predicates.permission_predicates as predicates
from core import BotContext
from factories import UtilsFactory
from data_managers import DataUtils
from db_managers.data_classes import DbUserInfo
from discord_extension_stuff.extras import Extras


class LogicCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.db_manager = UtilsFactory.get_db_manager()
        self.extras = Extras(bot_context)

    @commands.command(name='config_change')
    @commands.check(predicates.check_is_trusted)
    async def config_change_command(self, ctx: Context, osu_user_id: int, osu_game_mode: str):
        """
        Changes the user's config parameters.

        Parameters:
            - osu_user_id (int)     : User id
            - osu_game_mode (str)   : 'osu', 'catch', 'taiko', 'mania'
        """
        user_info = DbUserInfo(ctx.author.id, osu_user_id, osu_game_mode)
        if not user_info.are_fields_valid():
            response = "Sorry, but specified fields are not valid"
        elif not await self.osu_api_utils.check_if_user_exists(user_info.osu_user_id):
            response = "Sorry, but osu user with specified id does not exist"
        else:
            await self.db_manager.users_table_manager.insert_user_info(user_info)
            response = (f"Successfully changed `osu_user_id` to {user_info.osu_user_id} and `osu_game_mode` to "
                        f"{user_info.osu_game_mode}")
        await ctx.reply(response)

    @commands.command(name='config_check')
    @commands.check(predicates.check_is_trusted)
    async def config_check_command(self, ctx: Context):
        """
        Prints out user's config.
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        response = f"Your `{user_info.osu_user_id=}` and `{user_info.osu_game_mode=}`"
        await ctx.send(response)

    @commands.command(name='trusted_users')
    async def trusted_users_command(self, ctx: Context):
        """
        Prints out trusted users list.
        """
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_trusted_users())
        response = f"Trusted users:\n{data_str}"
        await ctx.send(response)

    @commands.command(name='admins')
    async def admins_command(self, ctx: Context):
        """
        Prints out admins list.
        """
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_admin_users())
        response = f"Admin users:\n{data_str}"
        await ctx.send(response)

    @commands.command(name='add_trusted_user')
    @commands.check(predicates.check_is_admin)
    async def add_trusted_user_command(self, ctx: Context, *, user: discord.Member | int):
        """
        Adds trusted user.

        Parameters:
            - user (discord.Member | int) : Mention of a discord user OR user id
        """
        user_id = -1
        if isinstance(user, discord.Member):
            user_id = user.id
        elif isinstance(user, int):
            if not await self.extras.check_if_discord_user_exists(user):
                await ctx.reply("Discord user with specified id does not exist.")
                return

            user_id = user

        await DataUtils.add_trusted_user(user_id)
        response = f"User with id: {user_id} added to trusted users"
        await ctx.send(response)
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_trusted_users())
        response = f"Trusted users:\n{data_str}"
        await ctx.send(response)

    @commands.command(name='remove_trusted_user')
    @commands.check(predicates.check_is_admin)
    async def remove_trusted_user_command(self, ctx: Context, *, user: discord.Member | int):
        """
        Removes trusted user.

        Parameters:
            - user (discord.Member | int) : Mention of a discord user OR user id
        """
        user_id = -1
        if isinstance(user, discord.Member):
            user_id = user.id
        elif isinstance(user, int):
            user_id = user

        await DataUtils.remove_trusted_user(user_id)
        response = f"User with id: {user_id} was removed from trusted users"
        await ctx.send(response)
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_trusted_users())
        response = f"Trusted users:\n{data_str}"
        await ctx.send(response)
