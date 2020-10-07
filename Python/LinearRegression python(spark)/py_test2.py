df = spark.read.csv("dataset/Log_Reg_dataset.csv", inferSchema=True, header=True)
df.count()
len(df.columns)
df.printSchema()
df.show(5)
df.summary().show()
df.groupBy('Platform').count().show()
df.groupBy('Country').count().show()
df.groupBy('Status').count().show()
df.groupBy('Country').mean().show()
df.groupBy('Platform').mean().show()
df.groupBy('Status').mean().show()

from pyspark.ml.feature import StringIndexer, OneHotEncoder

platform_indexer = StringIndexer(inputCol='Platform',outputCol='Platform_Num').fit(df)
df = platform_indexer.transform(df)
df.show(5)

platform_encoder = OneHotEncoder(inputCol='Platform_Num', outputCol='Platform_Vector').fit(df)
df = platform_encoder.transform(df)
df.show(5)

df.groupBy('Platform').count().orderBy('count', ascending=False).show(5)
df.groupBy('Platform_Num').count().orderBy('count', ascending=False).show(5)
df.groupBy('Platform_Vector').count().orderBy('count', ascending=False).show(5)

platform_encoder = OneHotEncoder(inputCol='Platform_Num', outputCol='Platform_Vector').fit(df)
df = platform_encoder.transform(df)
df.show(5)

country_indexer = StringIndexer(inputCol='Country',outputCol='Country_Num').fit(df)
df = country_indexer.transform(df)

country_encoder = OneHotEncoder(inputCol='Country_Num',outputCol='Country_Vector').fit(df)
df = country_encoder.transform(df)
df.select(['Country', 'Country_Num', 'Country_Vector']).show(5)

from pyspark.ml.feature import VectorAssembler

df_assembler = VectorAssembler(inputCols=['Platform_Vector', 'Country_Vector', 'Age', 'Repeat_Visitor','Web_pages_viewed'], outputCol='features')
df = df_assembler.transform(df)

df.printSchema()

df.select(['features', 'Status']).show(5)

model_df = df.select(['features', 'Status'])

train_df, test_df = model_df.randomSplit([0.7, 0.3])

train_df.count()
test_df.count()

log_reg_model = LogisticRegression(labelCol='Status') 
log_reg_model_fit = log_reg_model.fit(train_df)

log_reg_model_fit.coefficients

log_reg_model_fit.intercept

train_result = log_reg_model_fit.evaluate(train_df).predictions

correct_preds = train_result.filter(train_result['Status']==1).filter(train_result['prediction']==1).count()

train_df.filter(train_df['Status']==1).count()

correct_preds

correct_preds/train_df.filter(train_df['Status']==1).count()

from pyspark.ml.evaluation import BinaryClassificationEvaluator

results = log_reg_model_fit.evaluate(test_df).predictions

results.select(['Status', 'prediction']).show(20)
