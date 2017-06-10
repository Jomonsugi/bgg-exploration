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

# def train_val_test(ugr_rdd):
#     training, validation, test = ugr_rdd.randomSplit([0.6, 0.2, 0.2], 34L)
#     validation_for_predict = validation.map(lambda x: (x[0], x[1]))
#     test_for_predict = test.map(lambda x: (x[0], x[1]))

def train_model(ugr_rdd):
    seed = 42L
    iterations = 10
    regularization_parameter = 0.1
    ranks = [4, 8, 12]
    errors = [0, 0, 0]
    err = 0
    tolerance = 0.02

    min_error = float('inf')
    best_rank = -1
    best_iteration = -1
    training, validation, test = ugr_rdd.randomSplit([0.6, 0.2, 0.2], 34L)
    validation_for_predict = validation.map(lambda x: (x[0], x[1]))
    test_for_predict = test.map(lambda x: (x[0], x[1]))
    for rank in ranks:
        model = ALS.train(training, rank, seed=seed, iterations=iterations,
                          lambda_=regularization_parameter)
        predictions = model.predictAll(validation_for_predict).map(lambda r: ((r[0], r[1]), r[2]))
        rates_and_preds = validation.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
        error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
        errors[err] = error
        err += 1
        print 'For rank %s the RMSE is %s' % (rank, error)
        if error < min_error:
            min_error = error
            best_rank = rank

    print 'The best model was trained with rank %s' % best_rank

def train_val_test_test(ugr_rdd):
    train, validation, test = ugr_rdd.randomSplit([6, 2, 2], seed=0L)
    validation_for_predict = validation.map(lambda x: (x[0], x[1]))
    test_for_predict = test.map(lambda x: (x[0], x[1]))
    return train, validation, test, validation_for_predict, test_for_predict

def predict_test(train, validation, test, validation_for_predict, test_for_predict):
    seed = 5L
    iterations = 10
    regularization_parameter = 0.1
    ranks = [4,8,12]
    errors = [0, 0, 0]
    err = 0
    tolerance = 0.02

    min_error = float('inf')
    best_rank = -1
    best_iteration = -1
    for rank in ranks:
        model = ALS.train(train, rank, seed=seed, iterations=iterations,
                          lambda_=regularization_parameter)
        predictions = model.predictAll(validation_for_predict).map(lambda r: ((r[0], r[1]), r[2]))
        rates_and_preds = validation.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
        error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
        errors[err] = error
        err += 1
        print 'For rank %s the RMSE is %s' % (rank, error)
        if error < min_error:
            min_error = error
            best_rank = rank

    print 'The best model was trained with rank %s' % best_rank
    return predictions, rates_and_preds

if __name__ == '__main__':
    ugr, ugr_rdd = mongo_to_rdd()
    # training, validation, test = train_val_test(ugr_rdd)
    # predictions, ratings_and_predictions = train_model(ugr_rdd)

    train, validation, test, validation_for_predict, test_for_predict = train_val_test_test(ugr_rdd)

    predictions, rates_and_preds = predict_test(train, validation, test, validation_for_predict, test_for_predict)
