import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context

import discord_extension_stuff.predicates.permission_predicates as predicates
from core import BotContext
from discord_extension_stuff.extras import Extras
from factories import UtilsFactory
from statistics_managers import BeatmapsetsUserStatisticManager


class OsuApiLogicCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.db_manager = UtilsFactory.get_discord_users_data_db_manager()
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.extras = Extras(bot_context)

    @commands.command(name='beatmapsets_stats')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    async def beatmapsets_stats_command(self, ctx: Context, *, query: str):
        """
        Get grade stats on certain group of beatmapsets.
        To stop the command, reply 'stop' to the 'Calculating...' message.

        Parameters:
            - query (str)   : The search query. Can include filters like ranked<2019.
            - mode          : Mode from your config by default.
        """
        user_info = await self.db_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.extras.calculate_beatmapsets_stats(query, user_info))
        is_task_completed = await self.extras.wait_till_task_complete(ctx, calc_task=calc_task)
        if is_task_completed:
            beatmapsets_stats: BeatmapsetsUserStatisticManager = calc_task.result()
            response = beatmapsets_stats.get_pretty_stats()
            await ctx.reply(response)
            image_bytes = beatmapsets_stats.get_bar_plot()
            image_file = discord.File(fp=image_bytes, filename=f"bar_plot.png")
            await ctx.reply(file=image_file)

    @commands.command(name='beatmap_playcount_slow')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    async def beatmap_playcount_slow_command(self, ctx: Context, *, beatmap_id: int):
        """
        Get user playcount on a beatmap by iterating over all MOST PLAYED beatmaps.
        To stop the command, reply 'stop' to the 'Calculating...' message.

        Parameters:
            - beatmap_id (int)
        """
        user_info = await self.db_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.osu_api_utils.get_user_beatmap_playcount(beatmap_id, user_info))
        is_task_completed = await self.extras.wait_till_task_complete(ctx, calc_task=calc_task)
        if is_task_completed:
            playcount = calc_task.result()
            response = f"You have `{playcount}` playcount on a `{beatmap_id}` beatmap"
            await ctx.reply(response)

    @commands.command(name='most_recent')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    async def most_recent_play_command(self, ctx: Context):
        """
        Get user's most recent play.
        """
        user_info = await self.db_manager.get_user_info(ctx.author.id)
        score = await self.osu_api_utils.get_user_most_recent_score(user_info)
        if score is not None:
            beatmapset_id = score.beatmapset.id
            beatmapset_title = score.beatmapset.title
            beatmap_url = score.beatmap.url
            embed = discord.Embed()
            embed.add_field(name="{}".format(score.user_id),
                            value="[{0}]({1})".format(beatmapset_title, beatmap_url))
            embed.set_thumbnail(url=f'https://assets.ppy.sh/beatmaps/{beatmapset_id}/covers/list.jpg')
            await ctx.reply(embed=embed)
        else:
            await ctx.reply("No score")
