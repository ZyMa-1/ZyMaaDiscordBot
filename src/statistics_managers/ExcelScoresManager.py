import pathlib

import openpyxl
import tempfile

from openpyxl.styles import Font
from ossapi import Score

from core import PathManager
from db_managers.data_classes import DbUserInfo
from factories import UtilsFactory


class ExcelScoresManager:
    def __init__(self, user_info: DbUserInfo):
        self.user_info = user_info
        self.file_extension = '.xlsx'

        self.db_manager = UtilsFactory.get_db_manager()

        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.sheet_name = 'Scores'

        self.temp_file_path = None

    async def retrieve_rows(self):
        header_row = ['Artist unicode',
                      'Title unicode',
                      'Diff name',
                      'Creator',
                      'Score',
                      'Mods',
                      'Accuracy']
        self.sheet.append(header_row)

        header_cell = self.sheet[1]

        for cell in header_cell:
            cell.font = Font(bold=True)

        async for score_info in self.db_manager.scores_table_manager.get_all_user_scores(self.user_info):
            score: dict = score_info.deserialize_score_json()

            # Check if 'beatmapset' and 'beatmap' keys exist before accessing nested keys
            artist_unicode = score.get('beatmapset', {}).get('artist_unicode') if score.get('beatmapset') else 'None'
            title_unicode = score.get('beatmapset', {}).get('title_unicode') if score.get('beatmapset') else 'None'
            version = score.get('beatmap', {}).get('version') if score.get('beatmap') else 'None'
            creator = score.get('beatmapset', {}).get('creator') if score.get('beatmapset') else 'None'
            score_value = score.get('score')
            mods_value = score.get('mods')
            accuracy = round(score.get('accuracy', 0) * 100, 2)

            row_data = [artist_unicode, title_unicode, version, creator, score_value, mods_value, accuracy]
            self.sheet.append(row_data)

    def save_workbook(self) -> pathlib.Path:
        temp_file = tempfile.NamedTemporaryFile(dir=PathManager.TEMP_DIR, delete=False, suffix=self.file_extension)
        self.workbook.save(temp_file.name)
        self.temp_file_path = pathlib.Path(temp_file.name)
        return self.temp_file_path

    def delete_temp_file(self):
        if self.temp_file_path:
            if self.temp_file_path.exists():
                try:
                    self.temp_file_path.unlink()
                except Exception as e:
                    raise e
                finally:
                    self.temp_file_path = None
