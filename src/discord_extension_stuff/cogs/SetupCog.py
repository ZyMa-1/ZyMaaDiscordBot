import logging

from discord.ext import commands

from core import BotContext

logger = logging.getLogger()  # root logger


class SetupCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot

    @commands.Cog.listener()
    async def on_ready(self):
        for cog_name, cog_class in self.bot.cogs.items():
            logger.info(f"Loaded cog: {cog_name}")
        logger.info(f'Logged in as {self.bot.user}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Respond when first entered a server.
        welcome_message = f"Hello! I am a mini Discord bot made by .zymaa"
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(welcome_message)
                break
