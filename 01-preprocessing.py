# ST446 - Big Data Analytics
# Preprocessing Script: Unzip, Load CSVs, Save Parquet

import warnings, os, shutil
warnings.filterwarnings('ignore')

from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("ST446-Preprocess").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    # 1. Unzip (temporary)
    zip_path = "data/RAW_monthly_data.zip"
    temp_extract = "data/monthly_data_temp/"
    
    print("Extracting ZIP...")
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_extract)
    
    # 2. Load CSVs
    print("Loading CSVs...")
    df = spark.read.option("header", "true").option("inferSchema", "true") \
                   .csv(f"{temp_extract}**/*.csv")  # Handles nested structure
    
    print(f"Loaded: {df.count():,} rows")
    
    # 3. Write Parquet
    print("Saving Parquet...")
    df.write.mode("overwrite").parquet("data/flights_partitioned/")
    
    # 4. CLEANUP: Delete temp extracted files
    print("Cleaning up temp files...")
    shutil.rmtree(temp_extract)
    
    print("Complete! data/flights_partitioned/ ready.")
    spark.stop()

if __name__ == "__main__":
    main()