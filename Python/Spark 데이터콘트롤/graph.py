from pyspark.sql.functions import expr
from pyspark.sql.functions import desc
from graphframes import GraphFrame

bikeStations = spark.read.option("header", "true")\
    .csv("dataset/201508_station_data.csv")
tripData = spark.read.option("header", "true")\
    .csv("dataset/201508_trip_data.csv")

# COMMAND ----------

stationVertices = bikeStations.withColumnRenamed("name", "id").distinct()
tripEdges = tripData\
    .withColumnRenamed("Start Station", "src")\
    .withColumnRenamed("End Station", "dst")



# $SPARK_HOME/bin/pyspark --packages graphframes:graphframes:0.8.1-spark3.0-s_2.12
# COMMAND ----------
# graphframes(https://spark-packages.org/package/graphframes/graphframes) 라이브러리가 필요합니다.
# http://graphframes.github.io/quick-start.html
# DataBricks Runtime: https://docs.databricks.com/user-guide/libraries.html#maven-libraries

stationGraph = GraphFrame(stationVertices, tripEdges)
stationGraph.cache()


37.774438, 128.938219
# COMMAND ----------

print("Total Number of Stations: " + str(stationGraph.vertices.count()))
print("Total Number of Trips in Graph: " + str(stationGraph.edges.count()))
print("Total Number of Trips in Original Data: " + str(tripData.count()))

# COMMAND ----------

stationGraph.edges.groupBy(
    "src", "dst").count().orderBy(desc("count")).show(10)

# COMMAND ----------

stationGraph.edges\
    .where("src = 'Townsend at 7th' OR dst = 'Townsend at 7th'")\
    .groupBy("src", "dst").count()\
    .orderBy(desc("count"))\
    .show(10)

# COMMAND ----------

townAnd7thEdges = stationGraph.edges\
    .where("src = 'Townsend at 7th' OR dst = 'Townsend at 7th'")
subgraph = GraphFrame(stationGraph.vertices, townAnd7thEdges)

# COMMAND ----------

motifs = stationGraph.find("(a)-[ab]->(b); (b)-[bc]->(c); (c)-[ca]->(a)")


spark.conf.set("spark.sql.legacy.timeParserPolicy","LEGACY")
# COMMAND ----------

motifs.selectExpr("*",
                  "to_timestamp(ab.`Start Date`, 'MM/dd/yyyy HH:mm') as abStart",
                  "to_timestamp(bc.`Start Date`, 'MM/dd/yyyy HH:mm') as bcStart",
                  "to_timestamp(ca.`Start Date`, 'MM/dd/yyyy HH:mm') as caStart")\
    .where("ca.`Bike #` = bc.`Bike #`").where("ab.`Bike #` = bc.`Bike #`")\
    .where("a.id != b.id").where("b.id != c.id")\
    .where("abStart < bcStart").where("bcStart < caStart")\
    .orderBy(expr("cast(caStart as long) - cast(abStart as long)"))\
    .selectExpr("a.id", "b.id", "c.id", "ab.`Start Date`", "ca.`End Date`")\
    .limit(1).show(1, False)

# COMMAND ----------

ranks = stationGraph.pageRank(resetProbability=0.15, maxIter=10)
ranks.vertices.orderBy(desc("pagerank")).select("id", "pagerank").show(10)

# COMMAND ----------

inDeg = stationGraph.inDegrees
inDeg.orderBy(desc("inDegree")).show(5, False)

# COMMAND ----------

outDeg = stationGraph.outDegrees
outDeg.orderBy(desc("outDegree")).show(5, False)

# COMMAND ----------

degreeRatio = inDeg.join(outDeg, "id")\
    .selectExpr("id", "double(inDegree)/double(outDegree) as degreeRatio")
degreeRatio.orderBy(desc("degreeRatio")).show(10, False)
degreeRatio.orderBy("degreeRatio").show(10, False)

# COMMAND ----------

stationGraph.bfs(fromExpr="id = 'Townsend at 7th'",
                 toExpr="id = 'Spear at Folsom'", maxPathLength=2).show(10, False)

# COMMAND ----------

spark.sparkContext.setCheckpointDir("/tmp/checkpoints")

# COMMAND ----------

minGraph = GraphFrame(stationVertices, tripEdges.sample(False, 0.1))
cc = minGraph.connectedComponents()


# COMMAND ----------

cc.where("component != 0").show()


# COMMAND ----------

scc = minGraph.stronglyConnectedComponents(maxIter=3)
scc.groupBy("component").count().show()

# COMMAND ----------