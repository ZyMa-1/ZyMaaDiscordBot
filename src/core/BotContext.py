from discord.ext.commands import Bot


class BotContext:
    """
    BotContext - Dependency injection for future scaling, maybe.
    """

    def __init__(self, bot):
        self.bot: Bot = bot

    def get_bot(self):
        return self.bot
