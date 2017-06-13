import pyspark as ps
from pymongo import MongoClient
import numpy as np
import random
from pyspark import SparkConf, SparkContext
from pyspark.ml.recommendation import ALS
from pyspark.sql import SQLContext
from pyspark.sql.functions import col
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Transformer
import math
import itertools
from math import sqrt
from operator import add
import sys
import time
from pyspark.sql.functions import UserDefinedFunction
from pyspark.sql.types import DoubleType
from pyspark.sql import Row
from pyspark.sql.types import *

spark = ps.sql.SparkSession.builder \
        .master("local[*]") \
        .appName("collab_rec") \
        .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/bgg.game_comments") \
        .getOrCreate()

sc = spark.sparkContext
sc.setCheckpointDir('checkpoint/')
sqlContext = SQLContext(sc)

def mongo_to_rdd_df():
    df = spark.read.format("com.mongodb.spark.sql.DefaultSource").load()
    ugr_data = df.select('user_id','game_id','rating').repartition(16).cache()
    ugr_df = ugr_data.filter("rating is not null")
    ugr_rdd = ugr_df.rdd
    ugr_df = ugr_df.withColumn("game_id", ugr_df["game_id"].cast("int"))
    return ugr_df, ugr_rdd

def train_val_test_df(ugr_df):
    (df_train, df_val, df_test) = ugr_df.randomSplit([0.6, 0.2, 0.2], seed=0L)
    return df_train, df_val, df_test

def make_evaluator():
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                    predictionCol="prediction")
    return evaluator

def computeRmse(model, data, evaluator):
    predictions = model.transform(data)
    predictions_drop = predictions.dropna()
    rmse = evaluator.evaluate(predictions_drop)
    print("Root-mean-square error = " + str(rmse))
    return rmse

def predict_test_df(df_train, df_val, evaluator):
    ranks = [5]
    lambdas = [0.2]
    numIters = [200]
    bestModel = None
    bestValidationRmse = float("inf")
    bestRank = 0
    bestLambda = -1.0
    bestNumIter = -1
    # df_train = df_train.na.drop()
    # df_val=df_val.na.drop()
    for rank, lmbda, numIter in itertools.product(ranks, lambdas, numIters):
        als = ALS(rank=rank, maxIter=numIter, regParam=lmbda, numUserBlocks=10, numItemBlocks=10, implicitPrefs=False,
                  alpha=1.0,
                  userCol="user_id", itemCol="game_id", seed=1, ratingCol="rating", nonnegative=True,
                  checkpointInterval=10, intermediateStorageLevel="MEMORY_AND_DISK", finalStorageLevel="MEMORY_AND_DISK")
        model=als.fit(df_train)

        validationRmse = computeRmse(model, df_val, evaluator)
        print "RMSE (validation) = {} for the model trained with rank: {}, lambda: {}, numIter: {} ".format(validationRmse, rank, lmbda, numIter)
        if (validationRmse < bestValidationRmse):
            bestModel = model
            bestValidationRmse = validationRmse
            bestRank = rank
            bestLambda = lmbda
            bestNumIter = numIter

    print('The best model was trained with \n rank: {} \n lambda: {} \n bestNumIter: {} \n RMSE: {}'.format(bestRank, bestLambda, bestNumIter, bestValidationRmse))
    optimized_model = bestModel
    return optimized_model

def df_predict(df_test, optimized_model):
    #optimized hyperparemeters from predict_test_df
    seed = 1
    rank = 5
    numIter = 200
    lmbda = 0.2

    predictions = optimized_model.transform(df_test)
    print(predictions.count())
    print(predictions.take(3))
    predictions_drop = predictions.dropna()
    print(predictions_drop.count())
    print(predictions_drop.take(10))
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
    rmse = evaluator.evaluate(predictions_drop)
    print(rmse)
    print 'RMSE for test data: {}'.format(rmse)
    return predictions

if __name__ == '__main__':
    ugr_df, ugr_rdd = mongo_to_rdd_df()
    df_train, df_val, df_test = train_val_test_df(ugr_df)
    evaluator = make_evaluator()
    optimized_model = predict_test_df(df_train, df_val, evaluator)
    df_predict(df_test, optimized_model)
