from pymongo import MongoClient
import string
import pickle

client = MongoClient()
coll = client.bgg.game_comments

games = list(coll.distinct('game'))

def caps():
    pretty_games = []
    for game in games:
        game = game.replace("-", " ")
        game = " ".join([string.capitalize(x) for x in game.split()])
        pretty_games.append(game)
    return pretty_games

def pretty_to_pickle(pretty_games):
    with open('data/pretty_games_p2.pkl', 'wb') as fp:
        pickle.dump(pretty_games, fp)


if __name__ == '__main__':
    pretty_games = caps()
    pretty_to_pickle(pretty_games)
