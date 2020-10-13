df = spark.read.format("csv")\
  .option("header", "true")\
  .option("inferSchema", "true")\
  .load("dataset/2010-12-10.csv")
df.printSchema()
df.createOrReplaceTempView("dfTable")

#lit 
df.select(lit(5), lit("five"), lit(5.0))
df.printSchema()

from pyspark.sql.functions import col

df.where(col("invoiceNo") != 536365)\
    .select("InvoiceNo", "Description")\
    .show(5, False)

from pyspark.sql.functions import instr
priceFilter = col("UnitPrice") > 600

descripFilter = instr(df.Description, "POSTAGE") >=1
df.where(df.StockCode.isin("DOT")).where(priceFilter | descripFilter).show()
