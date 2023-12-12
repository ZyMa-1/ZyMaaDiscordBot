from discord.ext import commands
from discord.ext.commands import is_owner, Context

from core import BotContext
from data_managers import DataUtils


class OwnerCog(commands.cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot

    @is_owner()
    @commands.command(name="add_admin")
    async def add_admin_command(self, ctx: Context, user: commands.MemberConverter):
        """
        Adds admin.

        Parameters:
            - user (commands.MemberConverter)
        """
        user_id: int = user.id

        await DataUtils.add_admin(user_id)
        response = f"User with id `{user_id}` added to admins"
        await ctx.reply(response)
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_admin_users())
        response = f"Admins:\n{data_str}"
        await ctx.reply(response)

    @is_owner()
    @commands.command(name="remove_admin")
    async def remove_admin_command(self, ctx: Context, user: commands.MemberConverter):
        """
        Adds admin.

        Parameters:
            - user (commands.MemberConverter)
        """
        user_id: int = user.id

        await DataUtils.remove_admin(user_id)
        response = f"User with id `{user_id}` removed from admins"
        await ctx.reply(response)
        data_str = await self.extras.format_discord_id_list(await DataUtils.load_admin_users())
        response = f"Admins:\n{data_str}"
        await ctx.reply(response)
