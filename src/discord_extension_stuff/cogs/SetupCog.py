import logging

import discord
from discord.ext import commands

from core import BotContext

logger = logging.getLogger()  # root logger


class SetupCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        # global cooldown not working :sob:
        self.global_cooldown = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Logs info and changes bots presence when it is fully loaded.
        """
        for cog_name, cog_class in self.bot.cogs.items():
            logger.info(f"Loaded cog: {cog_name}")
        logger.info(f'Logged in as {self.bot.user}')
        await self.bot.change_presence(activity=discord.Game(name='osu!'))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        Handles guild join event.
        """
        welcome_message = f"Hello! I am {self.bot.user}."
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(welcome_message)
                break

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        Handles command errors.
        """
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f'This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.')
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(f'Check failure (you have no permission). nyam-nyam-nyam 🐱\n{str(error)}')
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(f'Bad argument(s)\n{str(error)}')
        else:
            await ctx.reply(f'Something broke 😭\n{str(error)}')
