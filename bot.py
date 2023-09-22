import asyncio

import discord
from discord.ext import commands

import initialize_project  # Needs to be imported first
from BotContext import BotContext
from src.data_managers.DataUtils import DataUtils
from src.db_managers.DiscordUsersDataDbManager import DiscordUsersDataDbManager
from src.discord_extension_stuff.MyHelpCommand import MyHelpCommand


async def add_cogs(bot, bot_context):
    import src.discord_extension_stuff.cogs as cogs
    await bot.add_cog(cogs.SetupCog(bot_context))
    await bot.add_cog(cogs.FunCog(bot_context))
    await bot.add_cog(cogs.LogicCog(bot_context))
    await bot.add_cog(cogs.BeatmapsetsStatsCog(bot_context))


async def run_bot(bot):
    await bot.start(DataUtils.load_discord_bot_token())


async def main():
    await initialize_project.initialize_resources()
    db_manager = DiscordUsersDataDbManager()
    await db_manager.create_users_table()

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.presences = True

    bot = commands.Bot(command_prefix='^', intents=intents)
    bot.help_command = MyHelpCommand()

    bot_context = BotContext(bot)

    await add_cogs(bot, bot_context)
    await run_bot(bot)


if __name__ == "__main__":
    asyncio.run(main())

