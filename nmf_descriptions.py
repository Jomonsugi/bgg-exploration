from sklearn.decomposition import NMF as NMF_sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
import pickle
import numpy as np
import matplotlib.pylab as plt

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

def do_nmf(V):
    nmf = NMF_sklearn(n_components=10, max_iter=100, random_state=34, alpha=.01, verbose = True)
    W = nmf.fit_transform(V)
    H = nmf.components_
    print('reconstruction error:', nmf.reconstruction_err_)
    return W, H

def do_nmf_loop(V):
    rec_err_lst = []
    for c in range(1,100):
        nmf = NMF_sklearn(n_components=c, max_iter=100, random_state=34, alpha=.01, verbose = True)
        W = nmf.fit_transform(V)
        H = nmf.components_
        print('reconstruction error:', nmf.reconstruction_err_)
        rec_err_lst.append(nmf.reconstruction_err_)
    return W, H, rec_err_lst

def topic_labels(H):
    hand_labels = []
    for i, row in enumerate(H):
        top_10 = np.argsort(row)[::-1][:10]
        print(top_10)
        print('topic', i)
        print('-->', ' '.join(vocabulary[top_10]))

def plot_bar(H, vocabulary):
    print("Plot highest weighted terms in basis vectors")
    for i, row in enumerate(H):
        top10 = np.argsort(row)[::-1][:10]
        print(top10)
        val = np.take(row, top10)
        print(val)
        plt.figure(i+1)
        plt.barh(np.arange(10) + .5, val, color="blue", align="center")
        print((vocabulary[top10]))
        plt.yticks(np.arange(10) + .5, (vocabulary[top10]))
        plt.xlabel("Weight")
        plt.ylabel("Term")
        plt.title("Highest Weighted Terms in Basis Vector W%d" % (i + 1))
        plt.grid(True)
        plt.savefig("plots/documents_basisW%d.png" % (i + 1), bbox_inches="tight")


def rec_error_plot(rec_err_lst):
    import matplotlib.pyplot as plt
    plt.plot(rec_err_lst)
    # plt.ylabel('some numbers')
    plt.savefig("plots/nmf_rec_error.png")

if __name__ == '__main__':
    plt.close("all")
    desc_processed = un_pickle()
    V, vocabulary = tfideffed(desc_processed)
    W, H = do_nmf(V)
    # W, H, rec_err_lst = do_nmf_loop(V)
    topic_labels(H)
    rec_error_plot(rec_err_lst)
    # plot_bar(H, vocabulary)
