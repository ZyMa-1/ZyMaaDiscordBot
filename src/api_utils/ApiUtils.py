import asyncio
from typing import List

from ossapi import Ossapi, BeatmapsetSearchResult
from ossapi.enums import Grade, BeatmapsetSearchMode

from src.models.BeatmapsetSearchResults import CombinedBeatmapsetSearchResult
from .RateLimiter import RateLimiter


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


class ApiUtils:
    def __init__(self, client_id, client_secret):
        self.ossapi = Ossapi(client_id, client_secret)
        self.time_period = 1
        self.max_requests = 2
        self.rate_limiter = RateLimiter(max_requests=self.max_requests, time_period=self.time_period)

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
            while not self.rate_limiter.can_make_request():  # bruh the rate limit thing turned out ugly
                asyncio.sleep(self.time_period)

            cur_res = self.ossapi.search_beatmapsets(*args, **kwargs)

            cursor = cur_res.cursor
            kwargs['cursor'] = cursor
            total_results.append(cur_res)
            if cursor is None or len(cur_res.beatmapsets) == 0 or cur_res.error is not None:
                return merge_beatmapset_search_results(total_results)

    def check_if_user_exists(self, user_id: int) -> bool:
        while not self.rate_limiter.can_make_request():  # bruh the rate limit thing turned out ugly
            asyncio.sleep(self.time_period)

        try:
            user = self.ossapi.user(user_id)
        except ValueError:  # User does not exist
            return False

        if user.id == user_id:
            return True

        return False

    def get_user_beatmap_score_grade(self, beatmap_id: int, user_id: int, mode: str) -> Grade | None:
        print("hello, im calcing grade", beatmap_id, user_id, mode)
        try:
            beatmap_user_score = self.ossapi.beatmap_user_score(beatmap_id, user_id, mode=mode)
        except ValueError:  # Score does not exist
            return None
        score_grade = beatmap_user_score.score.rank
        return score_grade
