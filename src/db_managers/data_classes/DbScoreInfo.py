from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DbScoreInfo:
    """
    Dataclass to wrap up and store all entries of the 'scores' database table.
    """

    id: Optional[int]
    user_info_id: int
    score_json_data: str
    timestamp: datetime = field(default_factory=datetime.now)
