import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context

import discord_extension_stuff.predicates.permission_predicates as predicates
from core import BotContext
from discord_extension_stuff.extras import DbExtras, DiscordExtras
from factories import UtilsFactory
from statistics_managers import BeatmapsUserGradesStatsManager


class OsuApiLogicCog(commands.Cog):
    def __init__(self, bot_context: BotContext):
        self.bot = bot_context.bot
        self.db_manager = UtilsFactory.get_db_manager()
        self.osu_api_utils = UtilsFactory.get_osu_api_utils()
        self.db_extras = DbExtras(bot_context)
        self.discord_extras = DiscordExtras(bot_context)

    @commands.command(name='beatmapsets_stats')
    @commands.check(predicates.check_is_trusted and predicates.check_is_config_set_up)
    @commands.cooldown(1, 60 * 10, commands.BucketType.user)
    async def beatmapsets_stats_command(self, ctx: Context, *, query: str):
        """
        Gets grade stats on a certain group of beatmapsets.

        Parameters:
            - query (str)     : The search query. Can include filters like `ranked<2019` or `artist=""some artist""`

        Example usage:
        1. beatmapsets_stats hyperpop
           query="hyperpop"
        """
        user_info = await self.db_manager.users_table_manager.get_user_info(ctx.author.id)
        calc_task = asyncio.create_task(self.db_extras.calculate_beatmapsets_grade_stats(query, user_info))
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60 * 4)

        if is_task_completed:
            stats: BeatmapsUserGradesStatsManager = calc_task.result()
            response = stats.get_pretty_stats()
            await ctx.reply(response)

            for p_name, p_bytes in await stats.get_all_plots():
                image_file = discord.File(fp=p_bytes, filename=f"{p_name}_plot.png")
                await ctx.reply(file=image_file)

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
        is_task_completed = await self.discord_extras.wait_till_task_complete(ctx, calc_task=calc_task,
                                                                              timeout_sec=60 * 60 * 2)
        if is_task_completed:
            beatmap_playcount = calc_task.result()
            title, artist, playcount = None, None, None
            if beatmap_playcount:
                playcount = beatmap_playcount.count
            if beatmap_playcount and beatmap_playcount.beatmapset:
                title = beatmap_playcount.beatmapset.title
                artist = beatmap_playcount.beatmapset.artist
            embed = discord.Embed()
            embed.add_field(name="{}".format(await user_info.osu_user_name()),
                            value="Your playcount: `{0}`".format(
                                playcount))
            embed.add_field(name="Beatmap(set)",
                            value="`{0}` - `{1}`".format(
                                title, artist))
            if beatmap_playcount.beatmapset:
                embed.set_thumbnail(
                    url=f'https://assets.ppy.sh/beatmaps/{beatmap_playcount.beatmapset.id}/covers/list.jpg')
            await ctx.reply(embed=embed)

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
            embed.add_field(name="{}".format(await user_info.osu_user_name()),
                            value="[{0}]({1})".format(beatmapset_title, beatmap_url))
            embed.set_thumbnail(url=f'https://assets.ppy.sh/beatmaps/{beatmapset_id}/covers/list.jpg')
            await ctx.reply(embed=embed)
        else:
            await ctx.reply("No score")
