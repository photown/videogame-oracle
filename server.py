from flask import Flask, render_template, request
from predictor.success_predictor import SuccessPredictor
from db.games_db import GamesDb
import datetime

app = Flask(__name__)

games_args = None


@app.route('/', methods=['GET', 'POST'])
def index():
    db = GamesDb()
    args = {}
    args['genres'] = games_args['genres']
    args['publishers'] = games_args['publishers']
    args['platforms'] = games_args['platforms']
    args['game_modes'] = games_args['game_modes']
    user_args = {}
    args['user_args'] = user_args
    if request.method == 'POST':
        print request.form

        valid_args_count = extract_user_arguments(user_args, games_args,
            request.form)
        min_args = 1
        if valid_args_count >= min_args:
            print "user_args = " + str(user_args)
            predictor = SuccessPredictor()
            average, confidence_interval = predictor.perform_cross_validation(
                games_args['games'], games_args, user_args)
            predictor_data = predictor.parse_data_for_predictor(
                user_args, games_args)
            prediction = predictor.predict(
                games_args['games'], games_args, predictor_data, user_args)
            args['prediction'] = ("{0:.2f}".format(
                prediction[0]), "{0:.2f}".format(average), confidence_interval)
            print "Prediction = " + str(prediction)
        else:
            args['error'] = 'At least %d attributes must be set.' % min_args

    return render_template('index.html', args=args)

def extract_user_arguments(user_args, games_args, form):
    for arg_name in request.form:
        if arg_name in ['genres', 'publishers', 'platforms', 'game_modes']:
            user_args[arg_name] = request.form.getlist(arg_name)
        elif arg_name in ['title', 'description', 'budget', 'release_date']:
            user_args[arg_name] = request.form[arg_name]

    valid_args_count = 0
    for arg_name in ['genres', 'publishers', 'platforms', 'game_modes']:
        if arg_name in user_args and type(user_args[arg_name]) is list \
                and set(user_args[arg_name]).issubset(games_args[arg_name]):
            valid_args_count += 1
        else:
            user_args[arg_name] = []

    if user_args['description']:
        valid_args_count += 1

    if user_args['budget']:
        try:
            float(user_args['budget'])
            valid_args_count += 1
        except ValueError:
            user_args['budget'] = ''

    if user_args['release_date']:
        try:
            datetime.datetime.strptime(user_args['release_date'], "%Y-%m-%d")
            valid_args_count += 1
        except ValueError:
            user_args['release_date'] = ''
    return valid_args_count

def get_common_keywords(all_keywords, n):
    keyword_to_count = {}
    for x in all_keywords:
        keyword = x['keyword']
        if keyword not in keyword_to_count:
            keyword_to_count[keyword] = 0
        keyword_to_count[keyword] += 1
    keywords_count_tuples = [(k, keyword_to_count[k])
                             for k in keyword_to_count]
    keywords_count_tuples.sort(key=lambda x: x[1], reverse=True)
    top_keywords = {keyword for keyword, _ in keywords_count_tuples[0:n]}
    return sorted(top_keywords)


def fill_keywords(games, keywords, all_keywords):
    for row in all_keywords:
        keyword = row['keyword']
        if keyword not in keywords:
            continue
        games[row['name']].add_keyword(keyword)


def read_data():
    db = GamesDb()
    games = db.query_all_games()
    return games


def init():
    global games
    global games_args
    games = read_data()

    db = GamesDb()
    all_keywords = db.query_all_keywords()
    keywords = get_common_keywords(all_keywords, 90)
    fill_keywords(games, keywords, all_keywords)

    games_args = {}
    games_args['genres'] = db.query_all_genres()
    games_args['publishers'] = db.query_all_publishers()
    games_args['platforms'] = db.query_all_platforms()
    games_args['game_modes'] = db.query_all_game_modes()
    games_args['keywords'] = keywords
    games_args['games'] = games

    app.run()

if __name__ == '__main__':
    init()
