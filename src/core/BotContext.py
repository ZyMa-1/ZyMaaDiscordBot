from discord.ext.commands import Bot


class BotContext:
    def __init__(self, bot):
        self.bot: Bot = bot

    def get_bot(self):
        return self.bot
