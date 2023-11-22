from typing import List

from ossapi import BeatmapsetSearchResult, BeatmapPlaycount, OssapiAsync, Score
from ossapi.enums import Grade, BeatmapsetSearchMode, UserBeatmapType, ScoreType

import my_logging.get_loggers
from db_managers.data_classes.DbUserInfo import DbUserInfo
from .TokenBucketRateLimiter import TokenBucketRateLimiter
from .models.CombinedBeatmapsetSearchResult import CombinedBeatmapsetSearchResult

logger = my_logging.get_loggers.osu_api_logger()


class OsuApiUtils:
    def __init__(self, client_id, client_secret):
        self.ossapi = OssapiAsync(client_id, client_secret)
        self.rate_limiter = TokenBucketRateLimiter(tokens_per_second=2.0)

    async def search_all_beatmapsets(self, *args, **kwargs) -> CombinedBeatmapsetSearchResult:
        """
        Search for beatmapsets using various criteria.

        Parameters:
            *args: Variable positional arguments for forwarding to search_beatmapsets.
            **kwargs: Variable keyword arguments for forwarding to search_beatmapsets.

        Returns:
            List[BeatmapsetSearchResult]: A list of BeatmapsetSearchResult objects.

        Forwards the search parameters to the search_beatmapsets function and collects the results.
        """
        match kwargs['mode']:
            case 'osu':
                kwargs['mode'] = BeatmapsetSearchMode.OSU
            case 'catch':
                kwargs['mode'] = BeatmapsetSearchMode.CATCH
            case 'mania':
                kwargs['mode'] = BeatmapsetSearchMode.MANIA
            case 'taiko':
                kwargs['mode'] = BeatmapsetSearchMode.TAIKO

        total_results = []
        while True:
            logger.info(f'{__name__}: {args=} {kwargs=}',
                        extra={'tokens_spent': 1.0})
            await self.rate_limiter.wait_for_request(tokens_required=1.0)
            cur_res = await self.ossapi.search_beatmapsets(*args, **kwargs)
            cursor = cur_res.cursor
            kwargs['cursor'] = cursor
            total_results.append(cur_res)
            if cursor is None or len(cur_res.beatmapsets) == 0 or cur_res.error is not None:
                return CombinedBeatmapsetSearchResult.merge_beatmapset_search_results(total_results)

    async def check_if_user_exists(self, user_id: int) -> bool:
        logger.info(f'{__name__}: {user_id=}',
                    extra={'tokens_spent': 1.0})
        try:
            await self.rate_limiter.wait_for_request(tokens_required=1.0)
            user = await self.ossapi.user(user_id)
        except ValueError:  # User does not exist
            return False

        if user.id == user_id:
            return True

        return False

    async def get_user_beatmap_score_grade(self, beatmap_id: int, user_info: DbUserInfo) -> Grade | None:
        logger.info(f'{__name__}: {beatmap_id=} { user_info.osu_user_id=} {user_info.osu_game_mode=}',
                    extra={'tokens_spent': 1.0})
        try:
            await self.rate_limiter.wait_for_request(tokens_required=1.0)
            beatmap_user_score = await self.ossapi.beatmap_user_score(beatmap_id, user_info.osu_user_id,
                                                                      mode=user_info.osu_game_mode)
        except ValueError:  # Score does not exist
            return None
        score_grade = beatmap_user_score.score.rank
        return score_grade

    async def get_user_beatmap_playcount(self, beatmap_id: int, user_info: DbUserInfo) -> int | None:
        offset = 0
        limit = 50
        while True:
            await self.rate_limiter.wait_for_request(tokens_required=1.0)
            logger.info(f'{__name__}: {beatmap_id=} { user_info.osu_user_id=} {user_info.osu_game_mode=}',
                        extra={'tokens_spent': 1.0})
            beatmap_playcount_list: List[BeatmapPlaycount] = (
                await self.ossapi.user_beatmaps(
                    user_info.osu_user_id, type=UserBeatmapType.MOST_PLAYED, limit=limit, offset=offset))

            if len(beatmap_playcount_list) == 0:
                return None

            for beatmap_playcount in beatmap_playcount_list:
                if beatmap_playcount.beatmap_id != beatmap_id:
                    continue

                return beatmap_playcount.count

            offset += limit

    async def get_user_most_recent_score(self, user_info: DbUserInfo) -> Score | None:
        logger.info(f'{__name__}: { user_info.osu_user_id=} {user_info.osu_game_mode=}',
                    extra={'tokens_spent': 1.0})
        await self.rate_limiter.wait_for_request(tokens_required=1.0)
        scores: List[Score] = await self.ossapi.user_scores(user_info.osu_user_id,
                                                            type=ScoreType.RECENT,
                                                            include_fails=True,
                                                            mode=user_info.osu_game_mode,
                                                            limit=1)
        return scores[0] if scores else None
