from extractor.sales_data_parser import SalesDataParser
from extractor.igdb import IgdbFetcher
import csv
import unicodecsv
import re
from db.games_db import GamesDb


def fetch_data(sales_data, igdb_fetcher):
    for x in sales_data.keys():
        print '---------------------------------'
        if not igdb_fetcher.get_game_info(sales_data[x]):
            del sales_data[x]
            continue
        print sales_data[x]


def populate_records():
    db = GamesDb()
    db.create_tables()
    db.insert_games(sales_data)

if __name__ == '__main__':
    sales_data_parser = SalesDataParser('extractor/sales.csv')
    sales_data = sales_data_parser.process()
    igdb_fetcher = IgdbFetcher()

    fetch_data(sales_data, igdb_fetcher)
    populate_records()
