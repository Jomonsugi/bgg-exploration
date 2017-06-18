from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
from pymongo import MongoClient
import pickle
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def get_data():
    client = MongoClient()
    db = client.bgg
    df = pd.DataFrame(list(db.game_stats.find()))
    return df

def mechanics(df):
    column_lst = list(df.columns.values)
    # print(column_lst)
    mechanics = [m for m in column_lst if 'mechanic' in m and m != 'mechanics']
    indexed_df = df.set_index(['game'])
    df_mechs = indexed_df[mechanics]
    for col in mechanics:
        df_mechs[col] = df_mechs[col] == True
    return df_mechs

def category(df):
    column_lst = list(df.columns.values)
    # print(column_lst)
    category = [c for c in column_lst if 'category' in c and c != 'categories']
    indexed_df = df.set_index(['game'])
    df_cats = indexed_df[category]
    for col in category:
        df_cats[col] = df_cats[col] == True
    return df_cats

def hamming(bool_df, df):
    distance_matrix = (1 - pairwise_distances(bool_df, metric = "hamming"))
    top_10 = list(distance_matrix[0].argsort()[:-10:-1])
    # print(df.iloc[top_10,149])
    return distance_matrix

def jaccard(bool_df, df):
    distance_matrix = (1 - pairwise_distances(bool_df, metric = "jaccard"))
    top_10 = list(distance_matrix[0].argsort()[:-10:-1])
    # print(df.iloc[top_10,149])
    return distance_matrix

def prep_columns(df):
    df = df[['Board Game Rank','game_id','game','description','playing_time','min_players', 'max_players', 'best_num_players', 'avg_rating', 'avg_weight', 'nmf', 'Game']]
    df.columns = ['Board Game Rank','game_id','game','Description','Playing Time','Min Players', 'Max Players', 'Best Num Players', 'avg_rating', 'Avg Weight', 'nmf', 'Game']
    return df

def un_pickle_labeled_df():
    with open('../data/nmf_labeled_df_p2.pkl', 'rb') as fp:
        nmf_labeled_df = pickle.load(fp)
    return nmf_labeled_df

def for_flask(board_game):
    nmf_labeled_df = un_pickle_labeled_df()
    choices = nmf_labeled_df['Game'].tolist()
    board_game = process.extract(board_game, choices, limit=1)
    board_game = board_game[0][0]
    df = get_data()
    df['nmf'] = nmf_labeled_df['nmf']
    df['Game'] = nmf_labeled_df['Game']
    df_mechs = mechanics(df)
    df_cats = category(df)
    mech_cat_df = pd.concat([df_mechs, df_cats], axis=1)
    distance_matrix = hamming(mech_cat_df, df)
    idx = int((df.Game[df.Game == board_game].index.tolist())[0])
    sorted_idx = list(distance_matrix[idx].argsort()[::-1])
    sorted_df = df.iloc[sorted_idx,:]
    rendered_df = prep_columns(sorted_df)
    rendered_df = rendered_df[['Game','Playing Time', 'Min Players', 'Max Players', 'Best Num Players' ,'Avg Weight']]
    return rendered_df.iloc[1:21,:], board_game

if __name__ == '__main__':
    rendered_df, board_game = for_flask(board_game)
