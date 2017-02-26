import unirest
import os
import datetime
from keyword_extractor import KeywordExtractor
import re

class IgdbFetcher:

    GET_GAME_INFO_TEMPLATE = "https://igdbcom-internet-game-database-v1.p.mashape.com/games/?fields=name,summary,storyline,publishers,themes,keywords,game_modes,genres,first_release_date,release_dates&limit=20&offset=0&search=%s"
    STOP_WORDS = {'game', 'player', 'gameplay'}

    def __init__(self):
        self.keyword_extractor = KeywordExtractor()

        self.publisher_id_to_name = {}
        self.platform_id_to_name = {}
        self.theme_id_to_name = {}
        self.genre_id_to_name = {}
        self.game_mode_id_to_name = {}
        self.game_keyword_id_to_name = {}

        self.fetch_publishers = self.__add_attr_to_game_data('publishers', 'companies', self.publisher_id_to_name)
        self.fetch_platforms = self.__add_attr_to_game_data('platform', 'platforms', self.platform_id_to_name)
        self.fetch_themes = self.__add_attr_to_game_data('themes', 'themes', self.theme_id_to_name)
        self.fetch_genres = self.__add_attr_to_game_data('genres', 'genres', self.genre_id_to_name)
        self.fetch_game_modes = self.__add_attr_to_game_data('game_modes', 'game_modes', self.game_mode_id_to_name)

    def get_game_info(self, game_data):

        response = unirest.get(self.GET_GAME_INFO_TEMPLATE % game_data.name,
          headers={
            "X-Mashape-Key": os.environ['IGDB_KEY'],
            "Accept": "application/json"
          }
        )
        game_info = None
        game_name_lower = game_data.name.lower().strip()
        for response_game in response.body:
            if not 'name' in response_game:
                continue
            if game_name_lower == response_game['name'].lower().strip():
                game_info = response_game
                break
        
        if not game_info:
            return False
        if not self.__validate_field(game_info, 'release_dates'):
            return False
        if not self.__validate_field(game_info, 'publishers'):
            return False
        if not self.__validate_field(game_info, 'themes') and not self.__validate_field(game_info, 'genres'):
            return False
        if not self.__validate_field(game_info, 'game_modes'):
            return False
        if not 'first_release_date' in game_info:
            return False
        if not 'summary' in game_info and not 'storyline' in game_info:
            return False

        for release_date in game_info['release_dates']:
            self.fetch_platforms(release_date, game_data.add_platform)

        if 'themes' in game_info:
            self.fetch_themes(game_info, game_data.add_genre)
        if 'genres' in game_info:
            self.fetch_genres(game_info, game_data.add_genre)
        
        self.fetch_publishers(game_info, game_data.add_publisher)
        self.fetch_game_modes(game_info, game_data.add_game_mode)
        
        release_date_timestamp = game_info['first_release_date']
        release_date = datetime.datetime.fromtimestamp(release_date_timestamp / 1000)
        game_data.release_date = release_date
        release_day_of_year = release_date.timetuple().tm_yday
        quarter = int(release_day_of_year / (367 / 4.0))
        game_data.release_quarter = quarter

        if 'summary' in game_info:
            summary = game_info['summary']
            summary_keywords = self.__extract_keywords(summary)
            game_data.add_keywords(summary_keywords)

        if 'storyline' in game_info:
            storyline = game_info['storyline']
            storyline_keywords = self.__extract_keywords(storyline)
            game_data.add_keywords(storyline_keywords)

        print "response body = " + str(response.body)
        return True

    def __validate_field(self, game_info, field_name):
        return field_name in game_info and len(game_info[field_name]) > 0

    def __is_valid_keyword(self, keyword):
        return keyword not in self.STOP_WORDS and re.match("^[A-Za-z]+$", keyword)

    def __extract_keywords(self, text):
        keyword_tuples = self.keyword_extractor.extract(text)
        keywords = []
        for keyword, _, _ in keyword_tuples:
            if self.__is_valid_keyword(keyword):
                keywords.append(keyword)
        return keywords

    def __add_attr_to_game_data(self, attr_name, endpoint_name, attr_map):
        def f(game_info, add_func):
            print "game_info bitch " + str(game_info) + " attr_name = " + attr_name
            if not attr_name in game_info:
                print "Attribute %s is empty, skipping." % attr_name
                return;
            if type(game_info[attr_name]) == list:
                for attr_id in game_info[attr_name]:
                    if not attr_id in attr_map:
                        fetched_name = self.__fetch_endpoint(endpoint_name, attr_id)
                        if not fetched_name:
                            continue
                        attr_map[attr_id] = fetched_name
                    add_func(attr_map[attr_id])
            else:
                attr_id = game_info[attr_name]
                if not attr_id in attr_map:
                    fetched_name = self.__fetch_endpoint(endpoint_name, attr_id)
                    attr_map[attr_id] = fetched_name
                add_func(attr_map[attr_id])
        return f

    def __fetch_endpoint(self, endpoint_name, id):
        response = unirest.get("https://igdbcom-internet-game-database-v1.p.mashape.com/%s/%s?fields=name" % (endpoint_name, id),
          headers={
            "X-Mashape-Key": os.environ['IGDB_KEY']
          }
        )
        if not type(response.body) == list or len(response.body) == 0 or not 'name' in response.body[0]:
            return None
        return response.body[0]['name']

