import csv
from model.data_model import DataModel


class SalesDataParser:

    COLUMN_NAME = 0
    COLUMN_SOLD_UNITS = 5
    COLUMN_BUDGET = 6

    def __init__(self, csv):
        self.csv = csv
        self.name_to_data = {}

    def process(self):
        with open(self.csv) as f:
            csv_reader = csv.reader(f)
            next(csv_reader)  # skip first row with titles
            for row in csv_reader:
                if not self.__is_row_valid(row):
                    continue
                name = row[self.COLUMN_NAME]
                if name in self.name_to_data:
                    game_data = self.name_to_data[name]
                    game_data.sold_units += float(row[self.COLUMN_SOLD_UNITS])
                else:
                    game_data = DataModel()
                    game_data.name = name

                    game_data.budget = float(row[self.COLUMN_BUDGET])
                    game_data.sold_units = float(row[self.COLUMN_SOLD_UNITS])
                    self.name_to_data[name] = game_data
        return self.name_to_data

    def __is_row_valid(self, row):
        for attr in row:
            if not attr:
                return False
        return True
