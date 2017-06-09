from sklearn.decomposition import NMF as NMF_sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
import pickle
import numpy as np

STOP = ['player', 'game']

def un_pickle():
    with open('data/doc_lst.pkl', 'rb') as fp:
        desc_processed = pickle.load(fp)
    return desc_processed

def tfideffed(desc_processed):
    tfidfvect = TfidfVectorizer(max_df = .5, min_df = 1, stop_words=STOP)
    tfidf = tfidfvect.fit_transform(desc_processed)
    vocabulary = np.array(tfidfvect.get_feature_names())
    return tfidf, vocabulary

def do_nmf(X):
    nmf = NMF_sklearn(n_components=10, max_iter=100, random_state=34, alpha=0.0, verbose = True)
    W = nmf.fit_transform(X)
    H = nmf.components_
    print('reconstruction error:', nmf.reconstruction_err_)
    #
    # for i in rand_articles:
    #     analyze_article(i, contents, web_urls, W, hand_labels)
    return W, H

def topic_labels(H):
    hand_labels = []
    for i, row in enumerate(H):
        top_twenty = np.argsort(row)[::-1][:20]
        print('topic', i)
        print('-->', ' '.join(vocabulary[top_twenty]))

if __name__ == '__main__':
    desc_processed = un_pickle()
    X, vocabulary = tfideffed(desc_processed)
    W, H = do_nmf(X)
    topic_labels(H)
