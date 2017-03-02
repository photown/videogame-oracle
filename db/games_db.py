import sqlite3
from model.data_model import DataModel


class GamesDb:

    def __init__(self):
        self.connection = sqlite3.connect('db/game_data.db')
        self.connection.row_factory = self.dict_factory

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create_tables(self):
        with open('db/games_db.schema') as schema:
            self.connection.executescript(schema.read())

    def insert_games(self, games):
        if len(games) == 0:
            return
        game_rows = []
        keywords = []
        publishers = []
        platforms = []
        game_modes = []
        genres = []
        for key in games:
            game = games[key]
            game_rows.append((game.name, game.budget, game.sold_units,
                              game.release_quarter, game.release_date))
            keywords.extend([(game.name, key) for key in game.keywords])
            publishers.extend([(game.name, publisher)
                               for publisher in game.publishers])
            platforms.extend([(game.name, platform)
                              for platform in game.platforms])
            game_modes.extend([(game.name, game_mode)
                               for game_mode in game.game_modes])
            genres.extend([(game.name, genre) for genre in game.genres])
        cursor = self.connection.cursor()
        cursor.executemany(
            'INSERT INTO games (name, budget, sold_units, release_quarter,'
            'release_date) VALUES (?, ?, ?, ?, ?)', game_rows)
        cursor.executemany(
            'INSERT INTO games_keywords (game_id, keyword)'
            'VALUES (?, ?)', keywords)
        cursor.executemany(
            'INSERT INTO games_publishers (game_id, publisher)'
            'VALUES (?, ?)', publishers)
        cursor.executemany(
            'INSERT INTO games_platforms (game_id, platform)'
            'VALUES (?, ?)', platforms)
        cursor.executemany(
            'INSERT INTO games_game_modes (game_id, game_mode)'
            'VALUES (?, ?)', game_modes)
        cursor.executemany(
            'INSERT INTO games_genres (game_id, genre)'
            'VALUES (?, ?)', genres)
        self.connection.commit()

    ''' Queries all records with full information without the keywords. '''

    def query_all_games(self):
        cursor = self.connection.cursor()
        rows = cursor.execute(
            'SELECT name, budget, sold_units, release_quarter, release_date, '
            'publisher, platform, game_mode, genre FROM games '
            'INNER JOIN games_publishers '
            'ON games_publishers.game_id = games.name '
            'INNER JOIN games_platforms '
            'ON games_platforms.game_id = games.name '
            'INNER JOIN games_game_modes '
            'ON games_game_modes.game_id = games.name '
            'INNER JOIN games_genres '
            'ON games_genres.game_id = games.name'
            )

        games = {}
        for game in rows:
            name = game['name']
            if name in games:
                model = games[name]
            else:
                model = DataModel()
                games[name] = model

            model.name = name
            model.genres.add(game['genre'])
            model.publishers.add(game['publisher'])
            model.platforms.add(game['platform'])
            model.game_modes.add(game['game_mode'])
            model.budget = game['budget']
            model.sold_units = game['sold_units']
            model.release_quarter = game['release_quarter']
            model.release_date = game['release_date']

        return games

    def query_all_keywords(self):
        cursor = self.connection.cursor()
        rows = cursor.execute(
            'SELECT name, keyword FROM games INNER JOIN games_keywords '
            'ON games.name = games_keywords.game_id')
        return rows.fetchall()

    def query_all_platforms(self):
        cursor = self.connection.cursor()
        rows = cursor.execute(
            'SELECT DISTINCT platform FROM games_platforms ORDER BY platform')
        return [row['platform'] for row in rows.fetchall()]

    def query_all_genres(self):
        cursor = self.connection.cursor()
        rows = cursor.execute(
            'SELECT DISTINCT genre FROM games_genres ORDER BY genre')
        return [row['genre'] for row in rows.fetchall()]

    def query_all_game_modes(self):
        cursor = self.connection.cursor()
        rows = cursor.execute(
            'SELECT DISTINCT game_mode FROM games_game_modes '
            'ORDER BY game_mode')
        return [row['game_mode'] for row in rows.fetchall()]

    def query_all_publishers(self):
        cursor = self.connection.cursor()
        rows = cursor.execute(
            'SELECT DISTINCT publisher FROM games_publishers '
            'ORDER BY publisher')
        return [row['publisher'] for row in rows.fetchall()]

    def dispose(self):
        self.connection = None
