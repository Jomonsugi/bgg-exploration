from libbgg.apiv2 import BGG
from datetime import datetime
import re
from operator import itemgetter
from pymongo import MongoClient
import pickle
import numpy as np
import time
from collections import defaultdict
import requests
from bs4 import BeautifulSoup


error_lst = []
def get_ratings_comments_results(ratings_coll):
    for game_id in call_id_lst:
        with open('data/pickles/user_dict_091617.pkl', 'rb') as fp:
            user_dict = pickle.load(fp)
        print(len(user_dict))
        # current_game = id_game_dict.get(current_id)
        print("current_id:", game_id)
        # print("current_game:", current_game)
        #specify starting page number, should be 1 unless testing
        page = 1
        while page != None:
            time.sleep(np.random.choice(random_sec))
            print("page:", page)
            r1 = requests.get("https://www.boardgamegeek.com/xmlapi2/thing?id="+str(game_id)+"&ratingcomments=1&page="+str(page)+"&pagesize=100")
            print(r1)
            soup = BeautifulSoup(r1.text, "xml")
            # print(soup)
            name = soup.findAll("name")
            current_game = name[0]["value"]
            print(current_game)
            ratings = soup.findAll("comments")
            # l = comment.findAll('comment')
            for entry in ratings:
                entry = entry
            tags = entry.findAll("comment")
            if tags:
                for tag in tags:
                    try:
                        rating = tag['rating']
                        if len(rating) == 0:
                            rating = None
                    except:
                        rating = None
                    try:
                        username = tag['username']
                        print(username)
                        if len(username) == 0:
                            username == None
                    except:
                        username == None
                    try:
                        comment = tag['value']
                        if len(value) == 0:
                            comment = None
                    except:
                        comment = None
                    if user_dict.get(username):
                        user_id = user_dict.get(username)
                        print("from dictionary:",user_id)
                    else:
                        try:
                            r2 = requests.get("https://www.boardgamegeek.com/xmlapi2/user?name="+username)
                            soup = BeautifulSoup(r2.text, "xml")
                            user_id = soup.findAll('user')[0]["id"]
                            user_dict[username]=user_id
                            time.sleep(np.random.choice(random_sec))
                            print("from api:",user_id)
                        except:
                            print("user id request on 1st try:")
                            print("page:", page)
                            print("game:", current_game)
                            raise ValueError('Error while calling API for user id')

                    ratings_coll.update_one({"game_id": game_id },
                                    {'$set' : {"game": current_game,
                                    "game": current_game,
                                    "game_id": str(game_id),
                                    "user_id" : str(user_id),
                                    "username": username,
                                    "rating": int(rating),
                                    "comment": comment
                                        }}, upsert=True)
                page += 1
            else:
                with open('data/pickles/user_dict_091617.pkl', 'wb') as fp:
                    pickle.dump(user_dict, fp)
                page = None


if __name__ == '__main__':
    conn = BGG()
    random_sec = np.random.uniform(5,6,[10000,])
    #open pickle file with ids,games,rating for use
    with open('data/game_ids_170516.pkl','rb') as fp:
        id_game_lst = pickle.load(fp)

    client = MongoClient()
    #database for comments to go into
    database = client.bgg
    #collection for stats variables to go in
    ratings_coll = database.game_ratings

    # id_game_dict = {x[0] : x[1] for x in id_game_lst[:-1]}
    #reverse lookup for dictionary
    # next(key for key, value in id_game_dict.items() if value == 'tzolk-mayan-calendar')

    #this range identifies the games that will be databased from the #id_game_lst
    call_id_lst = [x[0] for x in id_game_lst[:1]]
    get_ratings_comments_results(ratings_coll)
