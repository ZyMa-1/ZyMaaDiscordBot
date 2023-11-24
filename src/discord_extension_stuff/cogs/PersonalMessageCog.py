import discord
from discord.ext import commands

from core import BotContext


class PersonalMessageCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Some extra message handling"""
        if message.author == self.bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            # If user writes non-command message to the bots DMs, send the following message.
            if not message.content.startswith(self.bot.command_prefix) and not message.reference:
                await message.channel.send(
                    f"I do not understand you. Type `{str(self.bot.command_prefix)}help` for help")

        # await self.bot.process_commands(message)
