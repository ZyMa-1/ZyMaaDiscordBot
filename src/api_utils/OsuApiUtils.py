from typing import List

from ossapi import Ossapi, BeatmapsetSearchResult
from ossapi.enums import Grade, BeatmapsetSearchMode

import my_logging.get_loggers
from db_managers.data_classes.DbUserInfo import DbUserInfo
from .RateLimiter import rate_limit
from .models.CombinedBeatmapsetSearchResult import CombinedBeatmapsetSearchResult

logger = my_logging.get_loggers.osu_api_logger()


def merge_beatmapset_search_results(results: List[BeatmapsetSearchResult]) -> CombinedBeatmapsetSearchResult:
    return CombinedBeatmapsetSearchResult(
        beatmapsets=[s for r in results for s in r.beatmapsets],
        total=sum(r.total for r in results),
        errors=[r.error for r in results],
        search=results[0].search,
        recommended_difficulty=results[0].recommended_difficulty,
        cursor=None,
        cursor_string=None
    )


class OsuApiUtils:
    def __init__(self, client_id, client_secret):
        self.ossapi = Ossapi(client_id, client_secret)

    @rate_limit(max_requests=2, per_seconds=1)
    def search_all_beatmapsets(self, *args, **kwargs) -> CombinedBeatmapsetSearchResult:
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
            logger.info(f'ossapi.search_beatmapsets: {args=} {kwargs=}')
            cur_res = self.ossapi.search_beatmapsets(*args, **kwargs)
            cursor = cur_res.cursor
            kwargs['cursor'] = cursor
            total_results.append(cur_res)
            if cursor is None or len(cur_res.beatmapsets) == 0 or cur_res.error is not None:
                return merge_beatmapset_search_results(total_results)

    @rate_limit(max_requests=2, per_seconds=1)
    def check_if_user_exists(self, user_id: int) -> bool:
        logger.info(f'ossapi.user: {user_id=}')
        try:
            user = self.ossapi.user(user_id)
        except ValueError:  # User does not exist
            return False

        if user.id == user_id:
            return True

        return False

    @rate_limit(max_requests=2, per_seconds=1)
    def get_user_beatmap_score_grade(self, beatmap_id: int, user_info: DbUserInfo) -> Grade | None:
        logger.info(f'ossapi.beatmap_user_score: {beatmap_id=} { user_info.osu_user_id=} {user_info.osu_game_mode=}')
        try:
            beatmap_user_score = self.ossapi.beatmap_user_score(beatmap_id, user_info.osu_user_id,
                                                                mode=user_info.osu_game_mode)
        except ValueError:  # Score does not exist
            return None
        score_grade = beatmap_user_score.score.rank
        return score_grade

    @rate_limit(max_requests=2, per_seconds=1)
    def get_user_beatmap_playcount(self, beatmap_id: int, user_id: int, mode: str):
        pass
