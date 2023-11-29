from typing import List, Optional, Any

from ossapi import Beatmapset, BeatmapsetSearchResult


class CombinedBeatmapsetSearchResult:
    """
    Class to work with multiple 'BeatmapsetSearchResult' ossapi models.
    """

    def __init__(self,
                 beatmapsets: List[Beatmapset],
                 total: int,
                 errors: Optional[List[str]],
                 search: Any,
                 recommended_difficulty: Optional[float],
                 cursor=None,
                 cursor_string=None):
        self.beatmapsets = beatmapsets
        self.total = total
        self.errors = errors
        self.search = search
        self.recommended_difficulty = recommended_difficulty
        self.cursor = cursor
        self.cursor_string = cursor_string

    @staticmethod
    def merge_beatmapset_search_results(results: List[BeatmapsetSearchResult]):
        """
        Merges List[BeatmapsetSearchResult] into 'CombinedBeatmapsetSearchResult'
        """
        return CombinedBeatmapsetSearchResult(
            beatmapsets=[s for r in results for s in r.beatmapsets],
            total=sum(r.total for r in results),
            errors=[r.error for r in results],
            search=results[0].search,
            recommended_difficulty=results[0].recommended_difficulty,
            cursor=None,
            cursor_string=None
        )
