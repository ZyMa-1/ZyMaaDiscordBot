import logging
from difflib import get_close_matches
from typing import Dict

import discord
from discord.ext import commands

from core import BotContext

logger = logging.getLogger()  # root logger
command_usage: Dict[str, int] = {}


class ListenersCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot

    @commands.Cog.listener()
    async def on_ready(self):
        for cog_name, cog_class in self.bot.cogs.items():
            logger.info(f"Loaded cog: {cog_name}")
        logger.info(f'Logged in as {self.bot.user}')
        await self.bot.change_presence(activity=discord.Game(name='osu!'))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        welcome_message = f"Hello! I am {self.bot.user}."
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(welcome_message)
                break

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            mistyped_command = ctx.message.content.split(' ')[0][1:]
            valid_commands = [command.name for command in self.bot.commands]

            closest_match = get_close_matches(mistyped_command, valid_commands, n=1, cutoff=0.6)

            if closest_match:
                suggestion = closest_match[0]
                await ctx.reply(f"Command not found. Did you mean `{suggestion}`?")
            else:
                await ctx.reply("Command not found. Please check your command.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f'This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.')
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(f'Check failure (you have no permission 🐱)\n{str(error)}')
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(f'Bad argument(s)\n{str(error)}')
        else:
            await ctx.reply(f'Something broke 😭\n{str(error)}')

    @commands.Cog.listener()
    async def on_command(self, ctx):
        command_name = ctx.command.qualified_name
        if command_name not in command_usage:
            command_usage[command_name] = 1
        else:
            command_usage[command_name] += 1
