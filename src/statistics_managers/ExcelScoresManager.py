import pathlib

import openpyxl
import tempfile

from openpyxl.styles import Font
from ossapi import Score

from core import PathManager
from db_managers.data_classes import DbUserInfo
from factories import UtilsFactory


class ExcelWriter:
    def __init__(self, user_info: DbUserInfo, file_extension='.xlsx'):
        self.user_info = user_info
        self.file_extension = file_extension

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
        header_cell = self.sheet.append(header_row)
        for cell in header_cell[0]:
            cell.font = Font(bold=True)

        async for score_info in self.db_manager.scores_table_manager.get_all_user_scores(self.user_info):
            score: Score = score_info.deserialize_score_json()
            try:
                row_data = [score.beatmapset.artist_unicode,
                            score.beatmapset.title_unicode,
                            score.beatmap.version,
                            score.beatmapset.creator,
                            score.score,
                            round(score.accuracy * 100, 2)]
                self.sheet.append(row_data)
            except ValueError:
                row_data = [None] * len(header_row)
                self.sheet.append(row_data)

    def save_workbook(self) -> pathlib.Path:
        temp_file = tempfile.NamedTemporaryFile(dir=PathManager.TEMP_DIR, delete=False, suffix=self.file_extension)
        self.workbook.save(temp_file.name)
        self.temp_file_path = pathlib.Path(temp_file.name)
        return self.temp_file_path

    def delete_temp_file(self):
        if self.temp_file_path:
            try:
                self.temp_file_path.unlink()
            except Exception as e:
                raise e
            finally:
                self.temp_file_path = None
