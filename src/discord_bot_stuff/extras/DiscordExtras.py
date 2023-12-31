import asyncio
from asyncio import Task
from typing import List

import discord
from discord import Message
from discord.ext.commands import Context

from core import BotContext


class DiscordExtras:
    """
    Class designed to mix things up!
    """

    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot

    async def wait_for_reply(self, ctx: Context, start_msg: Message, *, reply_message_content: str,
                             timeout: int) -> bool:
        """
        Waits for the reply on certain message.
        Returns True if reply happened, False if not.
        """
        def check_reply(msg: Message):
            return (
                    msg.author == ctx.author
                    and msg.channel == ctx.channel
                    and msg.reference
                    and msg.reference.message_id == start_msg.id
                    and msg.content.lower() == reply_message_content
            )
        try:
            await self.bot.wait_for("message", check=check_reply, timeout=timeout)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            return False
        return True

    async def format_discord_id_list(self, discord_user_ids: List[int]) -> str:
        """
        Adds extra info to the 'discord_user_id_list' and returns ready to be printed string.
        Used for 'trusted_users' and 'admins' commands.
        """
        user_info_list = []

        for user_id in discord_user_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                user_info = (user.id, user.name)
                user_info_list.append(user_info)
            except discord.NotFound:
                user_info_list.append((user_id, "User not found"))
            except discord.HTTPException:
                user_info_list.append((user_id, "Error fetching user"))

        user_info_formatted = '\n'.join([str(item) for item in user_info_list])
        return user_info_formatted

    async def wait_till_task_complete(self, ctx: Context, *, calc_task: Task, timeout_sec: int = 3600) -> bool:
        """
        Creates a task that can be terminated by a discord user.
        Handles interaction between discord user and bot.
        Returns True If the task was completed, False otherwise.

        Further scaling of 'wait_for_reply'.
        """
        start_msg = await ctx.reply("Calculating... (reply stop to stop)")
        wait_for_reply_task = asyncio.create_task(
            self.wait_for_reply(ctx, start_msg, reply_message_content='stop', timeout=timeout_sec))
        done, pending = await asyncio.wait([calc_task, wait_for_reply_task], return_when=asyncio.FIRST_COMPLETED)

        await start_msg.delete()
        for task in pending:
            task.cancel()
        if calc_task in done:
            return True
        else:
            response = "Calculation canceled"
            await ctx.reply(response)
            return False
