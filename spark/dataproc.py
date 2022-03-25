import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, IntegerType, DateType, StructField, StringType, TimestampType


#!/usr/bin/env python

"""BigQuery I/O PySpark example."""

from pyspark.sql import SparkSession

spark = SparkSession \
  .builder \
  .master('yarn') \
  .appName('ghcnd') \
  .getOrCreate()

# Use the Cloud Storage bucket for temporary BigQuery export data used
# by the connector.
bucket = "ghcnd_raw"
spark.conf.set('temporaryGcsBucket', bucket)

df = spark.read.format('bigquery')\
.option('project','ghcn-d')\
.option('dataset','ghcnd') \
.option('table','stations').load()

df.show()

df. \
    write \
    .format("bigquery") \
    .mode("overwrite") \
    .option("project", 'ghcn-d') \
    .option("dataset", 'ghcnd') \
    .option("table", "test"). \
    save()
 
