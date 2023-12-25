import asyncio
from typing import List, Tuple

import discord
from discord.ext import commands
from discord.ext.commands import Context

import discord_extension_stuff.predicates.permission_predicates as predicates
from core import BotContext
from discord_extension_stuff.extras import Extras
from factories import UtilsFactory
from statistics_managers import BeatmapsUserGradesStatsManager


class OsuApiLogicCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.db_manager = UtilsFactory.get_db_manager()
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.extras = Extras(bot_context)

    @commands.command(name='beatmapsets_stats')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    @commands.cooldown(1, 60 * 10, commands.BucketType.user)
    async def beatmapsets_stats_command(self, ctx: Context, *, query: str):
        """
        Gets grade stats on a certain group of beatmapsets.

        Parameters:
            - query (str)     : The search query. Can include filters like `ranked<2019` or `artist=""some artist""`
            - plot_type (str) : 'no-graph' (default), 'bar', 'pie', 'bar&pie', 'pie&bar'.

        Example usage:
        1. beatmapsets_stats amogus pie
           query="amogus"
           plot_type="pie"

        2. beatmapsets_stats amogus not-a-pie
           query="amogus not-a-pie"
           plot_type="no-graph"

        3. beatmapsets_stats amogus pie&bar
           query="amogus"
           plot_type="pie&bar"
        """
        def process_query(_query: str) -> Tuple[str, List[str]]:
            def check_plot_types(_p_type_list: List[str]) -> bool:
                if len(set(_p_type_list)) != len(_p_type_list):
                    return False
                if not all(_ in {"bar", "pie"} for _ in _p_type_list):
                    return False
                return True

            _query_words = query.split()
            _last_word = _query_words[-1]
            _plot_types_list = _last_word.split('&')
            if check_plot_types(_plot_types_list):
                _query_words.pop()
            elif _last_word == 'no-graph':
                _plot_types_list = []
            else:
                _plot_types_list = []
            _modified_query = ' '.join(_query_words)
            return _modified_query, _plot_types_list

        async def send_plot(plot_type: str):
            image_bytes = None
            if plot_type == "bar":
                image_bytes = stats.get_bar_plot()
            elif plot_type == "pie":
                image_bytes = stats.get_pie_plot()

            if image_bytes:
                image_file = discord.File(fp=image_bytes, filename=f"{plot_type}_plot.png")
                await ctx.reply(file=image_file)

        query, p_types = process_query(query)

        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.extras.calculate_beatmapsets_grade_stats(query, user_info))
        is_task_completed = await self.extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                      timeout_sec=60 * 60 * 4)

        if is_task_completed:
            stats: BeatmapsUserGradesStatsManager = calc_task.result()
            response = stats.get_pretty_stats()
            await ctx.reply(response)

            for p_type in p_types:
                await send_plot(p_type)

    @commands.command(name='beatmap_playcount_slow')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    @commands.cooldown(1, 60 * 10, commands.BucketType.user)
    async def beatmap_playcount_slow_command(self, ctx: Context, *, beatmap_id: int):
        """
        Gets user's playcount on a beatmap by iterating over all MOST PLAYED beatmaps.

        Parameters:
            - beatmap_id (int)
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.osu_api_utils.get_user_beatmap_playcount(beatmap_id, user_info))
        is_task_completed = await self.extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                      timeout_sec=60 * 60 * 2)
        if is_task_completed:
            playcount = calc_task.result()
            response = f"You have `{playcount}` playcount on a `{beatmap_id}` beatmap"
            await ctx.reply(response)

    @commands.command(name='most_recent')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def most_recent_command(self, ctx: Context):
        """
        Gets user's most recent play.
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        score = await self.osu_api_utils.get_user_most_recent_score(user_info)
        if score is not None:
            beatmapset_id = score.beatmapset.id
            beatmapset_title = score.beatmapset.title_unicode
            beatmap_url = score.beatmap.url
            embed = discord.Embed()
            embed.add_field(name="{}".format(score.user_id),
                            value="[{0}]({1})".format(beatmapset_title, beatmap_url))
            embed.set_thumbnail(url=f'https://assets.ppy.sh/beatmaps/{beatmapset_id}/covers/list.jpg')
            await ctx.reply(embed=embed)
        else:
            await ctx.reply("No score")
