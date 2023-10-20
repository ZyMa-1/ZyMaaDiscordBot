import asyncio

from discord import Message
from discord.ext.commands import Context

from factories import UtilsFactory
from core import BotContext
from db_managers.data_classes.DbUserInfo import DbUserInfo
from statistics_managers import BeatmapsetsUserStatisticManager


class Extras:
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()

    # async def check_if_user_exists(self, ctx: Context, discord_user_id: int) -> bool:
    #     """Checks if user with specified discord_id exists."""
    #     # Try to fetch the user by their ID
    #     user = self.bot.get_user(discord_user_id)
    #
    #     if user is None:
    #         await ctx.reply(f"User with ID {discord_user_id} does not exist.")
    #         return False
    #
    #     return True

    async def calculate_beatmapsets_stats(self, query: str, user_info: DbUserInfo):
        """Calculates beatmapsets_stats."""
        combined_beatmapset_search_res = self.osu_api_utils.search_all_beatmapsets(query, mode=user_info.osu_game_mode)
        beatmapsets_stats = BeatmapsetsUserStatisticManager(combined_beatmapset_search_res.beatmapsets, user_info)
        await beatmapsets_stats.calculate_user_grades()
        return beatmapsets_stats

    # Meh, function below should work
    async def wait_for_reply(self, ctx: Context, start_msg: Message, *, reply_message_content: str,
                             timeout: int) -> bool:
        """Waits for the reply on certain message. Returns True if reply happened, False if not."""

        def check_reply(reply_message: Message):
            return (
                    reply_message.author == ctx.author
                    and reply_message.channel == ctx.channel
                    and reply_message.reference.message_id == start_msg.id
            )

        try:
            reply_msg = await self.bot.wait_for("message", check=check_reply, timeout=timeout)
            # If the user replied with `reply_message_content`, cancel the command
            if reply_msg.content == reply_message_content:
                return True  # Command was cancelled

        except asyncio.TimeoutError:
            pass  # No ^stop reply within the timeout

        return False  # Command was not cancelled
