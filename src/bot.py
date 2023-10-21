import discord
from discord.ext import commands

from core import BotContext
from data_managers import DataUtils
from discord_extension_stuff.MyHelpCommand import MyHelpCommand


async def add_cogs(bot, bot_context):
    import discord_extension_stuff.cogs as cogs
    await bot.add_cog(cogs.SetupCog(bot_context))
    await bot.add_cog(cogs.FunCog(bot_context))
    await bot.add_cog(cogs.LogicCog(bot_context))
    await bot.add_cog(cogs.OsuApiLogicCog(bot_context))


async def run_bot(bot):
    await bot.start(DataUtils.load_discord_bot_token())


async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.presences = True

    bot = commands.Bot(command_prefix='^', intents=intents)
    bot.help_command = MyHelpCommand()

    await add_cogs(bot, BotContext(bot))
    await run_bot(bot)
