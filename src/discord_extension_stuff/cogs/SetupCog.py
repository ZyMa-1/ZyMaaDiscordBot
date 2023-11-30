import logging

import discord
from discord.ext import commands

from core import BotContext

logger = logging.getLogger()  # root logger


class SetupCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.global_cooldown = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)

    @commands.Cog.listener()
    async def on_ready(self):
        for cog_name, cog_class in self.bot.cogs.items():
            logger.info(f"Loaded cog: {cog_name}")
        logger.info(f'Logged in as {self.bot.user}')
        logger.info(f'Global command cooldown set to rate={self.global_cooldown.rate} per={self.global_cooldown.per}')
        await self.bot.change_presence(activity=discord.Game(name='osu!'))

    @commands.Cog.listener()
    async def on_command(self, ctx):
        # Set global cooldown for all commands.
        bucket = self.global_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            await ctx.send(f"Command is on cooldown. Please try again in {retry_after:.2f} seconds.")
            raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.user)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Respond when first entered a server.
        welcome_message = f"Hello! I am a mini Discord bot made by .zymaa"
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(welcome_message)
                break
