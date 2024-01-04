import discord
from discord.ext import commands

from core import BotContext
from data_managers import DataUtils
from discord_extension_stuff.MyHelpCommand import MyHelpCommand


async def add_cogs(bot, bot_context):
    import discord_extension_stuff.cogs as cogs
    await bot.add_cog(cogs.ListenersCog(bot_context))
    await bot.add_cog(cogs.ChillCog(bot_context))
    await bot.add_cog(cogs.LogicCog(bot_context))
    await bot.add_cog(cogs.OsuApiLogicCog(bot_context))
    await bot.add_cog(cogs.PersonalMessageCog(bot_context))
    await bot.add_cog(cogs.BotStatsCog(bot_context))
    await bot.add_cog(cogs.ScoresStatsCog(bot_context))
    await bot.add_cog(cogs.OwnerCog(bot_context))


async def run_bot(bot):
    await bot.start(DataUtils.load_discord_bot_token())


async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.presences = True

    bot = commands.Bot(command_prefix='^', intents=intents)

    # Overwriting default help command
    bot.help_command = MyHelpCommand(verify_checks=False)  # IDK about that

    await add_cogs(bot, BotContext(bot))
    await run_bot(bot)
