import datetime
import pathlib
import tempfile
from typing import List

import openpyxl
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font
from ossapi import Mod

from core import PathManager
from db_managers.data_classes import DbUserInfo, DbScoreInfo
from factories import UtilsFactory


class ExcelScoresManager:
    def __init__(self, user_info: DbUserInfo, scores_info: List[DbScoreInfo]):
        self.user_info = user_info
        self.scores_info = scores_info

        self.file_extension = '.xlsx'
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d")
        self.sheet_name = f'Scores_{formatted_datetime}'
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active

        self.db_manager = UtilsFactory.get_db_manager()
        self.temp_file_path: pathlib.Path | None = None

    async def retrieve_rows(self):
        header_row = ['Beatmap link',
                      'Difficulty name',
                      'Score link',
                      'Mods',
                      'Accuracy',
                      'Scorev1']
        self.sheet.append(header_row)

        header_cell = self.sheet[1]

        for cell in header_cell:
            cell.font = Font(bold=True)

        for score_info in self.scores_info:
            score: dict = score_info.deserialize_score_json()

            # Check if 'beatmapset' and 'beatmap' keys exist before accessing nested keys
            score_id = score.get('id')
            score_v1 = score.get('score')
            beatmap_id = score.get('beatmap', {}).get('id') if score.get('beatmap') else 'None'
            version = score.get('beatmap', {}).get('version') if score.get('beatmap') else 'None'
            mods_value = score.get('mods')
            accuracy = round(score.get('accuracy', 0) * 100, 2)

            score_cell = WriteOnlyCell(self.sheet, value='=HYPERLINK("{}", "{}")'.
                                       format(f"https://osu.ppy.sh/scores/osu/{score_id}", score_id))
            score_cell.font = Font(color="0000FF", underline="single")

            beatmap_cell = WriteOnlyCell(self.sheet, value='=HYPERLINK("{}", "{}")'.
                                         format(f"https://osu.ppy.sh/b/{beatmap_id}", beatmap_id))
            beatmap_cell.font = Font(color="0000FF", underline="single")

            row_data = [beatmap_cell, version, score_cell, Mod(mods_value).short_name(), accuracy, score_v1]
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
