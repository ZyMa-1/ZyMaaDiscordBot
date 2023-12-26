from typing import List, Optional

from ossapi import BeatmapPlaycount, OssapiAsync, Score, BeatmapUserScore, User
from ossapi.enums import Grade, UserBeatmapType, ScoreType, BeatmapsetSearchMode, GameMode

import my_logging.get_loggers
from db_managers.data_classes import DbUserInfo
from .LeakyBucketRateLimiter import LeakyBucketRateLimiter
from .models import CombinedBeatmapsetSearchResult

logger = my_logging.get_loggers.osu_api_logger()


class OsuApiUtils:
    """
    Class to interact with 'ossapi' in various ways. 
    Extension of 'ossapi' for the needs.
    """

    def __init__(self, client_id, client_secret):
        self.ossapi = OssapiAsync(client_id, client_secret)
        self.rate_limiter = LeakyBucketRateLimiter(tokens_per_second=2.0, max_tokens=3.0)

    async def _log_and_process_request(self, *, tokens_required: float):
        await self.rate_limiter.process_request(tokens_required=tokens_required)
        logger.info(f'{self.__class__.__name__}:',
                    extra={'tokens_spent': tokens_required})

    async def search_all_beatmapsets(self, *args, **kwargs) -> CombinedBeatmapsetSearchResult:
        """
        Searches for beatmapsets using various criteria.
        Utilizes 'ossapi' 'search_beatmapsets' endpoint.

        Parameters:
            *args: Positional arguments for forwarding to 'search_beatmapsets' endpoint.
            **kwargs: Keyword arguments for forwarding to 'search_beatmapsets' endpoint.

        Returns:
            'CombinedBeatmapsetSearchResult' class instance.

        Forwards search parameters to the 'search_beatmapsets' function
        and collects cumulative results into 'CombinedBeatmapsetSearchResult' class.
        """
        match kwargs['mode']:
            case GameMode.OSU:
                kwargs['mode'] = BeatmapsetSearchMode.OSU
            case GameMode.CATCH:
                kwargs['mode'] = BeatmapsetSearchMode.CATCH
            case GameMode.MANIA:
                kwargs['mode'] = BeatmapsetSearchMode.MANIA
            case GameMode.TAIKO:
                kwargs['mode'] = BeatmapsetSearchMode.TAIKO

        total_results = []
        while True:
            await self._log_and_process_request(tokens_required=1.0)
            cur_res = await self.ossapi.search_beatmapsets(*args, **kwargs)
            cursor = cur_res.cursor
            kwargs['cursor'] = cursor
            total_results.append(cur_res)
            if cursor is None or len(cur_res.beatmapsets) == 0 or cur_res.error is not None:
                return CombinedBeatmapsetSearchResult.from_beatmapset_search_results(total_results)

    async def check_if_user_exists(self, user_id: int) -> bool:
        """
        Checks If user with specified 'user_id' exists.
        Utilizes 'ossapi' 'user' endpoint.
        """
        await self._log_and_process_request(tokens_required=1.0)
        try:
            user_res = await self.ossapi.user(user_id)
        except ValueError:  # User does not exist
            return False

        if user_res.id == user_id:
            return True

        return False

    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Returns 'ossapi' User instance for specified 'user_id'.
        Utilizes 'ossapi' 'user' endpoint.
        """
        await self._log_and_process_request(tokens_required=1.0)
        try:
            user = await self.ossapi.user(user_id)
            return user
        except ValueError:  # User does not exist
            return None

    async def get_user_beatmap_score_grade(self, beatmap_id: int, user_info: DbUserInfo) -> Optional[Grade]:
        """
        Gets grade of the user's top score on the given beatmap.
        Utilizes 'ossapi' 'beatmap_user_score' endpoint.
        """
        await self._log_and_process_request(tokens_required=1.0)
        try:
            beatmap_user_score: BeatmapUserScore = await self.ossapi.beatmap_user_score(beatmap_id,
                                                                                        user_info.osu_user_id,
                                                                                        mode=user_info.osu_game_mode)
        except ValueError:  # Score does not exist
            return None

        score_grade = beatmap_user_score.score.rank
        return score_grade

    async def get_user_beatmap_playcount(self, beatmap_id: int, user_info: DbUserInfo) -> Optional[int]:
        """
        Gets user's playcount on the given beatmap by iterating over ALL most played beatmaps.
        Utilizes 'ossapi' 'user_beatmaps' endpoint.
        """
        offset = 0
        limit = 100  # 100 is the max possible limit
        while True:
            await self._log_and_process_request(tokens_required=1.0)
            beatmap_playcount_list: List[BeatmapPlaycount] = (
                await self.ossapi.user_beatmaps(
                    user_info.osu_user_id, type=UserBeatmapType.MOST_PLAYED, limit=limit, offset=offset))

            if len(beatmap_playcount_list) == 0:
                return None

            for beatmap_playcount in beatmap_playcount_list:
                if beatmap_playcount.beatmap_id == beatmap_id:
                    return beatmap_playcount.count

            offset += limit

    async def get_user_most_recent_score(self, user_info: DbUserInfo) -> Optional[Score]:
        """
        Gets user's most recent score.
        Utilizes 'ossapi' 'user_scores' endpoint.
        """
        await self._log_and_process_request(tokens_required=1.0)
        scores: List[Score] = await self.ossapi.user_scores(user_info.osu_user_id,
                                                            type=ScoreType.RECENT,
                                                            include_fails=True,
                                                            mode=user_info.osu_game_mode,
                                                            limit=1)
        return scores[0] if scores else None

    async def get_all_user_beatmap_ids(self, user_info: DbUserInfo) -> List[int]:
        """
        Gets ALL beatmaps from the user's MOST_PLAYED section of the profile.
        Returns a list of beatmap_ids.
        Utilizes 'ossapi' 'user_beatmaps' endpoint.
        """
        offset = 0
        limit = 100  # 100 is the max possible limit
        beatmap_id_list = []
        while True:
            await self._log_and_process_request(tokens_required=1.0)
            beatmap_playcount_list: List[BeatmapPlaycount] = (
                await self.ossapi.user_beatmaps(
                    user_info.osu_user_id, type=UserBeatmapType.MOST_PLAYED, limit=limit, offset=offset))

            if len(beatmap_playcount_list) == 0:
                break

            for beatmap_playcount in beatmap_playcount_list:
                beatmap_id_list.append(beatmap_playcount.beatmap_id)

            offset += limit

        return beatmap_id_list

    async def get_beatmap_user_best_score(self, beatmap_id: int, user_info: DbUserInfo) -> Optional[Score]:
        """
        Gets the best user's score on a given beatmap.
        Utilizes 'ossapi' 'beatmap_user_score' endpoint.
        """
        await self._log_and_process_request(tokens_required=1.0)
        try:
            beatmap_user_score: BeatmapUserScore = await self.ossapi.beatmap_user_score(beatmap_id,
                                                                                        user_info.osu_user_id,
                                                                                        mode=user_info.osu_game_mode)
            return beatmap_user_score.score
        except ValueError:  # Score does not exist
            return None
