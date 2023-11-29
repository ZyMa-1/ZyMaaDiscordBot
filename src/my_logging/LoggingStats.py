import datetime
import glob
import re
from typing import List, Optional

import aiofiles

from core import PathManager


class LoggingStats:
    """
    Class for logging stats.
    """

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
        Calculates the amount of tokens spent between
        the present and (present - 'time_period_seconds') period of time.
        Stats are based on 'osu_api_utils' logging data files.
        """
        if time_period_seconds < 0 or time_period_seconds > 3600 * 24:
            raise RuntimeError("Function is not designed to work on that time_period yet.")

        current_time = datetime.datetime.now()
        total_tokens_spent = 0

        # Find log files matching the time period
        log_files_pattern = PathManager.OSU_API_LOGS_PATH / "osu_api*.log"
        log_files = glob.glob(str(log_files_pattern))
        log_files.sort(reverse=True)  # Sort in descending order to process the latest first

        for log_file_path in log_files:
            async with aiofiles.open(log_file_path, "r") as file:
                logs = await file.readlines()

            log_pattern = re.compile(
                r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*tokens_spent=(?P<tokens_spent>\d+)')

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
                        # No need to check further log files
                        break

        return total_tokens_spent
