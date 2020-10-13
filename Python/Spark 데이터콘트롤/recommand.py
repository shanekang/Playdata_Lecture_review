from pyspark.sql.functions import col, expr
from pyspark.mllib.evaluation import RankingMetrics, RegressionMetrics
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row

ratings = spark.read.text("dataset/sample_movielens_ratings.txt")\
    .rdd.toDF()\
    .selectExpr("split(value , '::') as col")\
    .selectExpr(
    "cast(col[0] as int) as userId",
    "cast(col[1] as int) as movieId",
    "cast(col[2] as float) as rating",
    "cast(col[3] as long) as timestamp")
training, test = ratings.randomSplit([0.8, 0.2])

# 사용자 선호에 대한 기본 신뢰도를 설정
Alpha = 10
# 분석하려는 데이터가 Implicit(true) 인지 Explicit(false) 인지 지정하는 값
implicitPrefs = False
# 사용자와 아이템을 학습하기 위한 특징 벡터의 차원
Rank = 10
# 총 학습 반복 횟수
MaxIter = 10
# 과적합 방지
RegParam = 0.01

als = ALS()\
    .setMaxIter(MaxIter)\
    .setAlpha(Alpha)\
    .setRegParam(RegParam)\
    .setRank(Rank)\
    .setRegParam(RegParam)\
    .setImplicitPrefs(implicitPrefs)\
    .setUserCol("userId")\
    .setItemCol("movieId")\
    .setRatingCol("rating")

als.explainParams()

alsModel = als.fit(training)
predictions = alsModel.transform(test)


# COMMAND ----------
# user와 Item간의 weight Factor
# Rank의 갯수에 따라서 달라진다.
alsModel.userFactors.show(10, False)

user_recs = alsModel.recommendForAllUsers(10)
user_recs.show()
user_recs.where(user_recs.userId == 12)\
    .select("recommendations.movieId", "recommendations.rating")\
    .collect()

item_recs = alsModel.recommendForAllItems(3)
item_recs.show()
item_recs.where(item_recs.movieId == 0)\
    .select("recommendations.userId", "recommendations.rating")\
    .collect()

user_subset = ratings.where(ratings.userId == 0)
user_subset.show()
user_subset_recs = alsModel.recommendForUserSubset(user_subset, 3)
user_subset_recs.first()
user_subset_recs.show()

user_subset_recs = alsModel.recommendForUserSubset(user_subset, 5)
user_subset_recs.first()
user_subset_recs.show()

alsModel.recommendForAllUsers(10)\
    .selectExpr("userId", "explode(recommendations)").show()
alsModel.recommendForAllItems(10)\
    .selectExpr("movieId", "explode(recommendations)").show()


# COMMAND ----------

evaluator = RegressionEvaluator()\
    .setMetricName("rmse")\
    .setLabelCol("rating")\
    .setPredictionCol("prediction")
rmse = evaluator.evaluate(predictions)
print("Root-mean-square error = %f" % rmse)

# COMMAND ----------
#실제 값
perUserActual = predictions\
    .where("rating > 2.5")\
    .groupBy("userId")\
    .agg(expr("collect_set(movieId) as movies")) 


# COMMAND ----------
#예측되어서 추천된 값
perUserPredictions = predictions\
    .orderBy(col("userId"), expr("prediction DESC"))\
    .groupBy("userId")\
    .agg(expr("collect_list(movieId) as movies"))


# COMMAND ----------

perUserActualvPred = perUserActual.join(perUserPredictions, ["userId"]).rdd\
    .map(lambda row: (row[1], row[2][:15]))
ranks = RankingMetrics(perUserActualvPred)


# COMMAND ----------
#평균치
ranks.meanAveragePrecision

#5개 보았을 때 평균치 이하이면 안된다는 기준으로 갯수를 정한다.
ranks.precisionAt(5)

# COMMAND ----------
