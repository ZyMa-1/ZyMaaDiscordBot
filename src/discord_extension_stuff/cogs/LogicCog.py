import asyncio

from discord.ext import commands
from discord.ext.commands import Context
from ossapi import GameMode

from BotContext import BotContext
from src.api_utils.ApiUtils import ApiUtils
from src.data_managers.DataUtils import DataUtils
from src.db_managers.DiscordUsersDataDbManager import DiscordUsersDataDbManager
from src.discord_extension_stuff.extras import Extras
import src.discord_extension_stuff.predicates as predicates
from src.statistics_managers.BeatmapsetsStatisticManager import BeatmapsetsUserStatisticManager


class LogicCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.api_utils = ApiUtils.get_instance()
        self.db_manager = DiscordUsersDataDbManager.get_instance()
        self.extras = Extras(bot_context)
        self.data_utils = DataUtils(bot_context)

    @commands.command(name='config_change')
    @commands.check(predicates.check_is_trusted)
    async def config_change_command(self, ctx: Context, osu_user_id: int, osu_game_mode: str):
        """
        Change user's config.

        Parameters:
        - osu_user_id (int): Number of the beers.
        - osu_game_mode (str): ['osu', 'taiko', 'catch', 'mania'].
        """
        if osu_game_mode not in [mode.value for mode in GameMode]:
            response = "Sorry, but specified game mode is not valid."
        elif not self.api_utils.check_if_user_exists(osu_user_id):
            response = "Sorry, but user with specified id does not exist."
        else:
            await self.db_manager.insert_user_info(ctx.author.name, osu_user_id, osu_game_mode)
            response = f"Successfully changed `osu_user_id` to {osu_user_id} and `osu_game_mode` to {osu_game_mode}"
        await ctx.reply(response)

    @commands.command(name='config_check')
    @commands.check(predicates.check_is_trusted)
    async def config_check_command(self, ctx: Context):
        """
        Prints out user's config values.
        """
        osu_user_id, osu_game_mode = await self.db_manager.get_user_info(ctx.author.name)
        response = f"Your `{osu_user_id=}` and `{osu_game_mode=}`"
        await ctx.send(response)

    @commands.command(name='trusted_users')
    async def trusted_users_command(self, ctx: Context):
        """
        Prints out list of trusted users.
        """
        response = f"Trusted users:\n{await self.data_utils.load_trusted_users(populate=True)}"
        await ctx.send(response)

    @commands.command(name='admins')
    async def admins_command(self, ctx: Context):
        """
        Prints out list of admin users.
        """
        response = f"Admin users:\n{await self.data_utils.load_admin_users(populate=True)}"
        await ctx.send(response)

    @commands.command(name='add_trusted_user')
    @commands.check(predicates.check_is_admin)
    async def add_trusted_user_command(self, ctx: Context, discord_user_id: int):
        """
        Adds trusted user by his Discord ID.
        """
        if await self.extras.check_if_user_exists(ctx, discord_user_id):
            await self.data_utils.add_trusted_user(discord_user_id)
            response = f"User with id:{discord_user_id} added to trusted users."
            await ctx.send(response)
            response = f"Trusted users:\n{await self.data_utils.load_trusted_users(populate=True)}"
            await ctx.send(response)

    @commands.command(name='remove_trusted_user')
    @commands.check(predicates.check_is_admin)
    async def remove_trusted_user_command(self, ctx: Context, discord_user_id: int):
        """
        Removes trusted user by his Discord ID.
        """
        if await self.extras.check_if_user_exists(ctx, discord_user_id):
            await self.data_utils.remove_trusted_user(discord_user_id)
            response = f"User with id:{discord_user_id} was removed from trusted users."
            await ctx.send(response)
            response = f"Trusted users:\n{await self.data_utils.load_trusted_users(populate=True)}"
            await ctx.send(response)
