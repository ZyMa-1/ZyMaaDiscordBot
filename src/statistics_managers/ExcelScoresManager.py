import io
from typing import List

import openpyxl
import os
import tempfile

from ossapi import Score

from core import PathManager


class ExcelWriter:
    def __init__(self, scores: List[Score], file_extension='.xlsx'):
        self.scores = scores
        self.file_extension = file_extension

        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.sheet_name = 'Scores'


    def write_headers(self):
        if not self.headers_written:
            for col_num, header in enumerate(self.column_order, 1):
                col_letter = openpyxl.utils.get_column_letter(col_num)
                self.sheet[f"{col_letter}1"] = header
            self.headers_written = True

    def write_data(self, data):
        self.sheet = self.workbook[self.sheet_name]
        self.write_headers()  # Ensure headers are written before data

        next_row = self.sheet.max_row + 1

        for col_num, col_name in enumerate(self.column_order, 1):
            col_letter = openpyxl.utils.get_column_letter(col_num)
            self.sheet[f"{col_letter}{next_row}"] = data.get(col_name, '')

    def save_workbook(self):
        with tempfile.NamedTemporaryFile(dir=PathManager.TEMP_DIR,
                                         delete=False,
                                         suffix=self.file_extension) as temp_file:
            self.workbook.save(temp_file.name)
            return temp_file.name
