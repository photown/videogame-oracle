# Videogame Oracle

Collects data (description, release quarter, genres, game modes, publishers, platforms, budget and sold copies) on 79 games and uses SVM to predict how many copies a user-entered game is likely to sell.

# Structure

The project is composed of 2 main modules - the data collection module and the client-server module.

The data collection module takes care of downloading all relevant information about the videogames. It first iterates over `sales.csv` which contains info about sold copies and manually added budgets about 79 of the games. Only the games with full information are considered for use in SVM. It uses the IGDB API to gather the rest of the required data about the games (description, release quarter, genres, game modes, publishers, platforms). `topia.termextract` library is used to extract all the nouns from the game descriptions. The 90 most common nouns through all games are being used in the input vector in SVM. All this data is put in a sqlite database. You start this module by running `python extract_data.py`.

The client-server module presents the user with a simple HTML form where he enters his game idea. Currently all fields are required, but it is subject to change. When the user presses Submit, using the `sklearn.svm` library, SVM for regression is performed. You start this module by running `python server.py`.

# Install
You need to install all dependencies using this snippet:  
`sudo apt-get install gfortran libopenblas-dev liblapack-dev python-dev numpy scikit-learn`

# Used resources  
http://www.vgchartz.com/gamedb/  
http://www.pixelprospector.com/the-big-list-of-game-revenue-sales/  
https://www.reddit.com/r/gamedev/comments/16zt7d/what_is_your_indie_game_budget/  
https://steamspy.com/  
https://en.wikipedia.org/wiki/List_of_most_expensive_video_games_to_develop  
http://kotaku.com/how-much-does-it-cost-to-make-a-big-video-game-1501413649  

# What to improve
1. More videogame data
2. A better way to determine most relevant keywords
3. Improve overall confidence
