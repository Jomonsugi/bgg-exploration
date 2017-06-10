import pyspark as ps
from pymongo import MongoClient
import numpy as np
import random
from pyspark import SparkConf, SparkContext
from pyspark.mllib.recommendation import ALS
from pyspark.sql import SQLContext
import math
import itertools

spark = ps.sql.SparkSession.builder \
        .master("local[2]") \
        .appName("collab_rec") \
        .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/bgg_test.game_comments_test") \
        .getOrCreate()

sc = spark.sparkContext
sqlContext = SQLContext(sc)

def mongo_to_rdd():
    df = spark.read.format("com.mongodb.spark.sql.DefaultSource").load()
    ugr_data = df.select('user_id','game_id','rating').repartition(16).cache()
    ugr = ugr_data.filter("rating is not null")
    ugr_rdd = ugr.rdd
    return ugr, ugr_rdd

def train_val_test_test(ugr_rdd):
    train, validation, test = ugr_rdd.randomSplit([6, 2, 2], seed=0L)
    validation_for_predict = validation.map(lambda x: (x[0], x[1]))
    test_for_predict = test.map(lambda x: (x[0], x[1]))
    return train, validation, test, validation_for_predict, test_for_predict

def predict_test(train, validation, test, validation_for_predict, test_for_predict):
    global bestRank
    global bestLambda
    global bestNumIter
    seed = 5L
    tolerance = 0.02
    min_error = float('inf')
    bestRank = 0
    bestLambda = -1.0
    bestNumIter = -1
    ranks = [4]
    lambdas = [0.1]
    numIters = [10,20]
    for rank, lmbda, numIter in itertools.product(ranks, lambdas, numIters):
        model = ALS.train(train, rank, numIter, lmbda)
        predictions = model.predictAll(validation_for_predict).map(lambda r: ((r[0], r[1]), r[2]))
        rates_and_preds = validation.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
        error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
        print 'rank: {}, lmbda: {}, numIter: {}, RMSE: {}'.format(rank, lmbda, numIter, error)
        if error < min_error:
            min_error = error
            bestRank = rank
            bestLambda = lmbda
            bestNumIter = numIter

    print 'The best model was trained with \n rank: {} \n lambda: {} \n bestNumIter: {} \n RMSE: {}'.format(bestRank, bestLambda, bestNumIter, min_error)
    return predictions, rates_and_preds

if __name__ == '__main__':
    ugr, ugr_rdd = mongo_to_rdd()
    # training, validation, test = train_val_test(ugr_rdd)
    # predictions, ratings_and_predictions = train_model(ugr_rdd)

    train, validation, test, validation_for_predict, test_for_predict = train_val_test_test(ugr_rdd)

    predictions, rates_and_preds = predict_test(train, validation, test, validation_for_predict, test_for_predict)
