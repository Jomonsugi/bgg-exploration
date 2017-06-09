import pyspark as ps
import pandas as pd
from pymongo import MongoClient
import pickle
import numpy as np
import random
from pyspark import SparkConf, SparkContext
from pyspark.mllib.recommendation import ALS
from pyspark.sql import SQLContext
import math
import itertools

#failing script, haven't figured out how to connect mongodb to spark

spark = ps.sql.SparkSession.builder \
        .master("local[2]") \
        .appName("collab_rec") \
        .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/bgg_test.game_comments_test") \
        .getOrCreate()

sc = spark.sparkContext
sqlContext = SQLContext(sc)
# uri = "mongodb://127.0.0.1/bgg.game_comments?readPreference=primaryPreferred"


if __name__ == '__main__':
    df = spark.read.format("com.mongodb.spark.sql.DefaultSource").load()
    ugr_data = df.select('user_id','game_id','rating').repartition(16).cache()
    ugr = ugr_data.filter("rating is not null")
