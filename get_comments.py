from libbgg.apiv2 import BGG
from datetime import datetime
import re
from operator import itemgetter
from pymongo import MongoClient
import pickle
import numpy as np
import time
from collections import defaultdict

#working, but need to figure out the best way to store the data as it loops
#to make an easily accessed schema in mongo
# in need id, game name, and all user/comments/ratings

def get_ratings_comments_results(call_id_lst):
    d = defaultdict(list)
    for game_id in call_id_lst:
        current_id = game_id
        page = 27
        while page != 0:
            comment_results = conn.boardgame(call_id_lst, comments=True, page=page, pagesize=100)
            time.sleep(np.random.choice(random_sec))
            try:
                comments = comment_results['items']['item']['comments']['comment']
                print("comments:" ,comments)
                for entry in comments:
                    d[game_id].append(entry)
                page += 1
            except KeyError:
                print("no comments")
                page = 0
    return d

if __name__ == '__main__':
    random_sec = np.random.uniform(5,7,[1000,])
    #open pickle file with ids,games,rating for use
    with open('data/game_ids_170516.pkl','rb') as fp:
        id_game_lst = pickle.load(fp)

    conn = BGG()
    id_game_dict = {x[0] : x[1] for x in id_game_lst[:-1]}
    call_id_lst = [x[0] for x in id_game_lst[:1]]
    rc_results = get_ratings_comments_results(call_id_lst)
