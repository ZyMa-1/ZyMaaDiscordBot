import discord
from discord.ext import commands
from discord.ext.commands import Context

import discord_extension_stuff.predicates.permission_predicates as predicates
from core import BotContext
from data_managers import DataUtils
from db_managers.data_classes import DbUserInfo
from discord_extension_stuff.converters import GameModeConverter, OsuUserIdConverter
from discord_extension_stuff.extras import Extras
from discord_extension_stuff.views import AcceptDeclineView
from factories import UtilsFactory


class LogicCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.db_manager = UtilsFactory.get_db_manager()
        self.extras = Extras(bot_context)

    @commands.command(name='config_change')
    @commands.check(predicates.check_is_trusted)
    async def config_change_command(self, ctx: Context, osu_user_id: OsuUserIdConverter,
                                    osu_game_mode: GameModeConverter):
        """
        Changes the user's config parameters.

        Parameters:
            - osu_user_id (int)     : Valid user id
            - osu_game_mode (str)   : 'osu', 'catch', 'taiko', 'mania'
        """
        user_info = DbUserInfo(ctx.author.id, osu_user_id, osu_game_mode)
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
        response = f"Your `osu_user_id` is {user_info.osu_user_id} and `osu_game_mode` is {user_info.osu_game_mode}"
        await ctx.reply(response)

    @commands.command(name='trusted_users')
    async def trusted_users_command(self, ctx: Context):
        """
        Prints out trusted users list.
        """
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_trusted_users())
        response = f"Trusted users:\n{data_str}"
        await ctx.reply(response)

    @commands.command(name='admins')
    async def admins_command(self, ctx: Context):
        """
        Prints out admins list.
        """
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_admin_users())
        response = f"Admins:\n{data_str}"
        await ctx.reply(response)

    @commands.command(name='add_trusted_user')
    @commands.check(predicates.check_is_admin)
    async def add_trusted_user_command(self, ctx: Context, user: commands.MemberConverter):
        """
        Adds trusted user.

        Parameters:
            - user (commands.MemberConverter)
        """
        user_id: int = user.id

        await DataUtils.add_trusted_user(user_id)
        response = f"User with id `{user_id}` added to trusted users"
        await ctx.reply(response)
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_trusted_users())
        response = f"Trusted users:\n{data_str}"
        await ctx.reply(response)

    @commands.command(name='remove_trusted_user')
    @commands.check(predicates.check_is_admin)
    async def remove_trusted_user_command(self, ctx: Context, user: commands.MemberConverter):
        """
        Removes trusted user.

        Parameters:
            - user (commands.MemberConverter)
        """
        user_id: int = user.id

        await DataUtils.remove_trusted_user(user_id)
        response = f"User with id `{user_id}` was removed from trusted users"
        await ctx.reply(response)
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_trusted_users())
        response = f"Trusted users:\n{data_str}"
        await ctx.reply(response)

    @commands.command(name='send_trusted_user_application')
    @commands.cooldown(1, 60 * 10, commands.BucketType.user)
    async def send_trusted_user_application_command(self, ctx: Context, *, application_message: str):
        """
        Sends trusted user application to the first admin DM and waits for the response.

        Parameters:
            - application_message (str) : Message of the application
        """
        if ctx.author.id in await DataUtils.load_trusted_users():
            await ctx.reply("You are already a trusted user")
            return

        start_msg = await ctx.reply("Your trusted user application is under consideration by the admin."
                                    "Wait for a response.")
        admin_user_id = await DataUtils.load_first_admin_user()
        if admin_user_id is None:
            await ctx.reply("There is no admins at all, no one can respond to the application")
            return

        embed = discord.Embed(title="Trusted User Application",
                              description=application_message,
                              color=discord.Color.blue())
        embed.add_field(name="Applicant Name", value=ctx.author.name, inline=True)
        embed.add_field(name="Applicant ID", value=ctx.author.id, inline=True)

        view = AcceptDeclineView(timeout=60 * 60 * 24)
        admin_dm_channel = await self.bot.get_user(admin_user_id).create_dm()
        admin_dm_msg = await admin_dm_channel.send(embed=embed, view=view)
        view.message = admin_dm_msg

        await view.wait()
        await start_msg.delete()

        # Notify the user about the decision
        if view.decision is True:
            await DataUtils.add_trusted_user(ctx.author.id)
            await ctx.reply("Your trusted user application has been accepted.")
        else:
            await ctx.reply("Your trusted user application has been declined.")
