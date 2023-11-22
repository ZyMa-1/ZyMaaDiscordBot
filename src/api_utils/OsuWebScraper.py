import asyncio
import os

import aiohttp

from core import PathManager


class OsuWebScraper:

    @staticmethod
    async def download_beatmap_cover(beatmap_id: int | str):
        """Returns path to the saved image or 'None'"""
        url = f"https://assets.ppy.sh/beatmaps/{beatmap_id}/covers/list.jpg"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.read()
                    if result is not None:
                        file_path = os.path.join(PathManager.TEMP_DIR, f"cover_{beatmap_id}.jpg")
                        with open(file_path, "wb") as f:
                            f.write(result)

                        return file_path

                return None

    @staticmethod
    async def delete_temp_files():
        async def delete_file(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                pass  # Pass for now!!!

        # Get a list of all files in the 'temp_dir' folder
        file_paths = [os.path.join(PathManager.TEMP_DIR, file_name) for file_name in os.listdir(PathManager.TEMP_DIR)]

        # Use asyncio.to_thread to delete files in a separate thread
        await asyncio.gather(*(delete_file(file_path) for file_path in file_paths))
