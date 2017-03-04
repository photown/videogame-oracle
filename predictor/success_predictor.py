from sklearn.svm import SVR
import numpy as np
import unicodecsv
import datetime
from sklearn.metrics import precision_score
from db.games_db import GamesDb
from extractor.keyword_extractor import KeywordExtractor
from random import shuffle


class SuccessPredictor:

    def __init__(self):
        self.keyword_extractor = KeywordExtractor()

    def predict(self, games, games_args, user_input_data, user_args):
        input_data, output_data = self.__extract_input_output_data(
            games, games_args, user_args)
        return self.__init_predictor(input_data, output_data, user_input_data)

    def perform_cross_validation(self, games, games_args, user_args):
        input_data, output_data = self.__extract_input_output_data(
            games, games_args, user_args)
        n = len(input_data)
        test_size = int(n * 0.2)
        accuracies = []
        bucket_size = 5  # +/- 5 million
        shuffled = zip(input_data, output_data)
        shuffle(shuffled)
        input_data = [pair[0] for pair in shuffled]
        output_data = [pair[1] for pair in shuffled]
        for i in range(0, 5):
            test_input_data = input_data[i * test_size:(i + 1) * test_size]
            test_output_data = output_data[i * test_size:(i + 1) * test_size]
            train_input_data = input_data[:i * test_size] \
                + input_data[(i + 1) * test_size:]
            train_output_data = output_data[:i * test_size] \
                + output_data[(i + 1) * test_size:]

            results = self.__init_predictor(
                train_input_data, train_output_data, test_input_data)

            for j in range(0, test_size):
                expected = test_output_data[j]
                actual = results[j]
                accuracies.append(
                    100 * int(abs(expected - actual) < bucket_size))
                print "Expected " + str(test_output_data[j]) + \
                    ", got " + str(results[j])
        average = reduce(lambda x, y: x + y, accuracies) / float(n)
        print "Cross validation result = " + str(average) + "%"
        return (average, bucket_size)

    def parse_data_for_predictor(self, user_args, game_args):
        publishers = user_args['publishers']
        platforms = user_args['platforms']
        genres = user_args['genres']
        game_modes = user_args['game_modes']
        description = user_args['description']
        release_date = user_args['release_date']
        budget = user_args['budget']

        keywords = self.keyword_extractor.extract(description)

        row = []
        if user_args['genres']:
            self.__add_listed_attribute(row, game_args['genres'], genres)
        if user_args['publishers']:
            self.__add_listed_attribute(row, game_args['publishers'], publishers)
        if user_args['platforms']:
            self.__add_listed_attribute(row, game_args['platforms'], platforms)
        if user_args['game_modes']:
            self.__add_listed_attribute(row, game_args['game_modes'], game_modes)
        if user_args['description']:
            self.__add_listed_attribute(row, game_args['keywords'], keywords)

        if release_date:
            date = datetime.datetime.strptime(release_date, "%Y-%m-%d")
            release_day_of_year = date.timetuple().tm_yday
            quarter = int(release_day_of_year / (367 / 4.0))
            row.append(quarter)

        if budget:
            row.append(float(budget))

        print "so now row is " + str(len(row)) + " and content is " + str(row)

        return [row]

    def __add_listed_attribute(self, row, all_items, game_items):
        attr_vec = [float(0)] * len(all_items)
        for item in game_items:
            if item in all_items:
                i = all_items.index(item)
                attr_vec[i] = float(1)
        row.extend(attr_vec)

    def __extract_input_output_data(self, games, games_args, user_args):
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
            if user_args['genres']:
                self.__add_listed_attribute(row, genres, game.genres)
            if user_args['publishers']:
                self.__add_listed_attribute(row, publishers, game.publishers)
            if user_args['platforms']:
                self.__add_listed_attribute(row, platforms, game.platforms)
            if user_args['game_modes']:
                self.__add_listed_attribute(row, game_modes, game.game_modes)
            if user_args['description']:
                self.__add_listed_attribute(row, keywords, game.keywords)
            if user_args['release_date']:
                row.append(game.release_quarter)
            if user_args['budget']:
                row.append(game.budget)
            input_data.append(row)
            output_data.append(game.sold_units)
        return (input_data, output_data)

    def __init_predictor(self, train_input_data, train_output_data,
                         input_data):
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
