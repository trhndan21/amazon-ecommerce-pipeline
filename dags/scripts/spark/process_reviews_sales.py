import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, regexp_replace, lower, lit, split, trim

def process_amazon_data(input_loc, output_loc):    
    # 1. Read data
    # multiLine=True (because review of Amazon often contains line breaks)
    df = spark.read \
        .option("header", True) \
        .option("multiLine", True) \
        .option("escape", "\"") \
        .csv(input_loc)

    # 2. Clean
    df_clean= df.withColumn("discounted_price", regexp_replace(col("discounted_price"), "[^0-9.]", "").cast("float")) \
                .withColumn("actual_price", regexp_replace(col("actual_price"), "[^0-9.]", "").cast("float")) \
                .withColumn("rating", col("rating").cast("float")) \
                .withColumn("category", trim(split(col("category"), "\|").getItem(0))) \
                .fillna({"review_content": "No review",})
    
    df_clean= df_clean.select("product_id", "product_name", "category", "discounted_price", "actual_price", "rating", "user_id", "review_content")

    # 3. Business logic (Transform)
    # (?i) is a flag for case-insensitive matching
    df_final= df_clean.withColumn("is_positive", when((col("rating") >= 4.0) |
                                                col("review_content").rlike("(?i)good|great|excellent|amazing|love|fantastic|perfect"),
                                                lit(True)).otherwise(lit(False)))

    # 4. Write data
    print(f"Writing data to: {output_loc}")
    df_final.write.mode("overwrite").parquet(output_loc)
    print("Job finished successfully!")


if __name__ == "__main__":
    # This part receives parameters from the command line (passed by Airflow)
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Input file path")
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()

    # This part starts Spark and connects to MinIO
    spark = (
        SparkSession.builder.appName("amazon-analytics")
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.2")
        .config("spark.hadoop.fs.s3a.access.key", "minio")
        .config("spark.hadoop.fs.s3a.secret.key", "minio123")
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") # Running inside Docker, so use 'minio'
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )

    process_amazon_data(args.input, args.output)