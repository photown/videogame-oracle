class DataModel:

    def __init__(self):
        self._name = None
        self._genres = set()
        self._publishers = set()
        self._platforms = set()
        self._budget = 0
        self._sold_units = 0
        self._keywords = set()
        self._game_modes = set()
        self._release_quarter = None
        self._release_date = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def genres(self):
        return self._genres

    def add_genre(self, genre):
        self._genres.add(genre)

    @property
    def publishers(self):
        return self._publishers

    def add_publisher(self, value):
        self._publishers.add(value)

    @property
    def platforms(self):
        return self._platforms

    def add_platform(self, value):
        self._platforms.add(value)

    @property
    def game_modes(self):
        return self._game_modes

    def add_game_mode(self, value):
        self._game_modes.add(value)

    @property
    def budget(self):
        return self._budget

    @budget.setter
    def budget(self, value):
        self._budget = value

    @property
    def sold_units(self):
        return self._sold_units

    @sold_units.setter
    def sold_units(self, value):
        self._sold_units = value

    @property
    def release_quarter(self):
        return self._release_quarter

    @release_quarter.setter
    def release_quarter(self, value):
        self._release_quarter = value

    @property
    def release_date(self):
        return self._release_date

    @release_date.setter
    def release_date(self, value):
        self._release_date = value

    @property
    def keywords(self):
        return self._keywords

    def add_keyword(self, keyword):
        self._keywords.add(keyword)

    def add_keywords(self, keywords):
        self._keywords.update(set(keywords))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'name: ' + str(self.name) + '\n' \
            'genres: ' + str(self.genres) + '\n' \
            'publishers: ' + str(self.publishers) + '\n' \
            'platforms: ' + str(self.platforms) + '\n' \
            'budget: ' + str(self.budget) + '\n' \
            'sold_units: ' + str(self.sold_units) + '\n' \
            'game_modes: ' + str(self.game_modes) + '\n' \
            'keywords: ' + str(self.keywords) + '\n' \
            'release_quarter: ' + str(self.release_quarter) + '\n' \
            'release_date: ' + str(self.release_date) + '\n'
