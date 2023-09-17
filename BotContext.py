from discord.ext.commands import Bot

from src.external_stuff import SingletonMeta


class BotContext(metaclass=SingletonMeta):
    def __init__(self, bot):
        self.bot: Bot = bot

    def get_bot(self):
        return self.bot
