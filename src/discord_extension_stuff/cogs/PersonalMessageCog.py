import discord
from discord.ext import commands
from discord.ext.commands import Context

from core import BotContext


class PersonalMessageCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            if not message.content.startswith(self.bot.command_prefix):
                await message.channel.send("I do not understand you. Type `^help` for help")

        await self.bot.process_commands(message)
