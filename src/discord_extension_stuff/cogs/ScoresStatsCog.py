from discord.ext import commands

from core import BotContext
import discord_extension_stuff.predicates.permission_predicates as predicates
from discord_extension_stuff.extras import Extras


class ScoresStatsCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.extras = Extras(bot_context)

    @commands.command(name='load_all_user_scores_to_db')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def load_all_user_scores_to_db_command(self):
        pass