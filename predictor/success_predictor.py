from sklearn.svm import SVR
import numpy as np
import unicodecsv
import datetime
from sklearn.metrics import precision_score
from db.games_db import GamesDb
from extractor.keyword_extractor import KeywordExtractor

class SuccessPredictor:

    def __init__(self):
        self.keyword_extractor = KeywordExtractor()

    def predict(self, games, games_args, input_data):
        input_data, output_data = self.__extract_input_output_data(games, games_args)
        return self.__init_predictor(input_data, output_data, input_data)

    def perform_cross_validation(self, games, games_args):
        input_data, output_data = self.__extract_input_output_data(games, games_args)
        n = len(input_data)
        test_size = int(n * 0.2)
        accuracies = []
        bucket_size = 5 # +/- 5 million
        for i in range(0, 5):
            test_input_data = input_data[i*test_size:(i+1)*test_size]
            test_output_data = output_data[i*test_size:(i+1)*test_size]
            train_input_data = input_data[:i*test_size] + input_data[(i+1)*test_size:]
            train_output_data = output_data[:i*test_size] + output_data[(i+1)*test_size:]
            
            results = self.__init_predictor(train_input_data, train_output_data, test_input_data)

            for j in range(0, test_size):
                expected = test_output_data[j]
                actual = results[j]
                accuracies.append(100 * int(abs(expected-actual) < bucket_size))
                print "Expected " + str(test_output_data[j]) + ", got " + str(results[j])
        average = reduce(lambda x, y: x + y, accuracies) / float(n)
        print "Cross validation result = " + str(average) + "%"
        return (average, bucket_size)    

    def parse_data_for_predictor(self, args, game_args):
        publishers = args['publishers']
        platforms = args['platforms']
        genres = args['genres']
        game_modes = args['game_modes']
        description = args['description']
        release_date = args['release_date']
        budget = float(args['budget'])
        date = datetime.datetime.strptime(release_date, "%Y-%m-%d")
        release_day_of_year = date.timetuple().tm_yday
        quarter = int(release_day_of_year / (367 / 4.0))

        keywords = self.keyword_extractor.extract(description)

        row = []
        self.__add_listed_attribute(row, game_args['genres'], genres)
        self.__add_listed_attribute(row, game_args['publishers'], publishers)
        self.__add_listed_attribute(row, game_args['platforms'], platforms)
        self.__add_listed_attribute(row, game_args['game_modes'], game_modes)
        self.__add_listed_attribute(row, game_args['keywords'], keywords)
        row.extend([quarter, budget])

        return [row]

    def __add_listed_attribute(self, row, all_items, game_items):
        attr_vec = [float(0)] * len(all_items)
        for item in game_items:
            if item in all_items:
                i = all_items.index(item)
                attr_vec[i] = float(1)
        row.extend(attr_vec)

    def __extract_input_output_data(self, games, games_args):
        genres = games_args['genres']
        publishers = games_args['publishers']
        platforms = games_args['platforms']
        game_modes = games_args['game_modes']
        keywords = games_args['keywords']
        input_data = []
        output_data = []

        for game_key in games:
            game = games[game_key]
            row = []
            self.__add_listed_attribute(row, genres, game.genres)
            self.__add_listed_attribute(row, publishers, game.publishers)
            self.__add_listed_attribute(row, platforms, game.platforms)
            self.__add_listed_attribute(row, game_modes, game.game_modes)
            self.__add_listed_attribute(row, keywords, game.keywords)
            row.extend([game.release_quarter, game.budget])

            input_data.append(row)
            output_data.append(game.sold_units)
        return (input_data, output_data)

    def __init_predictor(self, train_input_data, train_output_data, input_data):
        y = train_output_data
        X = train_input_data
        clf = SVR(C=100, epsilon=0.1, kernel='rbf')
        clf.fit(X, y)
        return self.__perform_prediction(input_data, clf)

    def __perform_prediction(self, input_data, clf):
        result = []
        for inp in input_data:
            inp = np.array(inp).reshape((1, -1))
            prediction = clf.predict(inp)
            result.extend(prediction)
        return result