#csv데이터를 데이터프래임으로 불러오기
adDF = spark.read.csv("dataset/Advertising.csv", inferSchema=True, header=True)
#데이터 위에서 5개 출력 해보자
adDF.show(5)
#데이터 총 갯수는?
adDF.count()

adDF.printSchema()

from pyspark.ml.feature import RFormula
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.linalg import Vectors

#transformer 라이브러리를 이용해서 벡터화 하는 방법
dataModel = RFormula().setFormula("Sales ~.").setFeaturesCol("features").setLabelCol("label")
model_fit = dataModel.fit(adDF).transform(adDF)

model_fit.show()
model_fit.printSchema()

model_fit_select = model_fit.select(["features","label"])

model_fit_select.show()
model_fit_select.printSchema()

#Vectors 함수를 이용해서 벡터화 하기
adV = adDF.rdd.map(lambda x: [Vectors.dense(x[0:3]), x[-1]]).toDF(['features', 'label'])

adV.show()
adV.printSchema()

# 회귀분석 모델을 적용하기
# lr = LinearRegression(featuresCol='features', labelCol='label', regParam = 0.3, elasticNetParam = 0.8)
lr = LinearRegression(featuresCol='features', labelCol='label')
lr_model = lr.fit(adV)
lr_model.save

#모델 적용하기
pred = lr_model.transform(adV)
pred.show(5)

#분석결과 보기
evaluator = RegressionEvaluator(predictionCol='prediction', labelCol='label')
evaluator.setMetricName('r2').evaluate(pred)

#테스트 셋과 트레이닝 셋으로 분리하기 1 
train, test = adV.randomSplit([0.7, 0.3])

lr = LinearRegression() 
lr_model = lr.fit(train)

testFit = lr_model.transform(test)

testFit.show()

