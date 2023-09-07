from typing import List, Optional, Any

from ossapi import Beatmapset


class CombinedBeatmapsetSearchResult:
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
