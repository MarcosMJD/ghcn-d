import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, IntegerType, DateType, StructField, StringType, TimestampType

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('ghcnd') \
    .config("credentialsFile", "/home/marcos/.google/credentials/ghcn-d-698480b9cb8d.json") \
    .getOrCreate()

df = spark.read.format('bigquery')\
.option('project','ghcn-d')\
.option('dataset','ghcnd') \
.option('table','stations').load()

df. \
    write \
    .format("bigquery") \
    .mode("overwrite") \
    .option("temporaryGcsBucket", 'ghcnd_raw') \
    .option("project", 'ghcdn-d') \
    .option("dataset", 'ghcdnd') \
    .option("table", "test"). \
    save()