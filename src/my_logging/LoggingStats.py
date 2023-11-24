import datetime
import re
from typing import List, Optional

import aiofiles

from core import PathManager


class LoggingStats:
    @staticmethod
    async def calculate_stats(time_periods: Optional[List[int]] = None):
        """
        Calculates stats in a given list of time frames counting from now to the past.
        Stats are based on 'osu_api_utils' logging data file. (file, not files)
        """
        if time_periods is None:
            time_periods = [60, 300, 3600, 24 * 3600]

        stats = {}
        for time_period_seconds in time_periods:
            tokens_spent = await LoggingStats.calculate_tokens_spent(time_period_seconds)
            stats[f'{time_period_seconds // 60}min'] = {
                'tokens_spent': tokens_spent,
            }

        return stats

    @staticmethod
    async def calculate_tokens_spent(time_period_seconds: int) -> int:
        """
        Calculates amount of token spent between period of time.
        Stats are based on 'osu_api_utils' logging data file. (file, not files)
        """
        if time_period_seconds < 0 or time_period_seconds > 3600 * 24:
            raise RuntimeError("Function does not designed to work on that time_period yet.")

        async with aiofiles.open(PathManager.OSU_API_MAIN_LOG_PATH, "r") as file:
            logs = await file.readlines()

        log_pattern = re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*tokens_spent=(?P<tokens_spent>\d+)')

        total_tokens_spent = 0
        current_time = datetime.datetime.now()

        for log_entry in reversed(logs):
            match = log_pattern.search(log_entry)
            if match:
                timestamp_str = match.group('timestamp')
                tokens_spent = int(match.group('tokens_spent'))

                # Parse the timestamp
                timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

                # Check If timestamp is within the time period
                if (current_time - timestamp).total_seconds() <= time_period_seconds:
                    total_tokens_spent += tokens_spent
                else:
                    break

        return total_tokens_spent
