"""
PySpark ETL Pipeline for E-Commerce Analytics
Main orchestration script
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from datetime import datetime
import sys
import os

# Database configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ecommerce_analytics")
POSTGRES_USER = os.getenv("POSTGRES_USER", "ecommerce_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ecommerce_pass")

# JDBC URL
JDBC_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
JDBC_PROPERTIES = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "driver": "org.postgresql.Driver"
}

# Data paths
DATA_DIR = "/app/data"
RAW_DATA_DIR = f"{DATA_DIR}/raw"
PROCESSED_DATA_DIR = f"{DATA_DIR}/processed"

def create_spark_session():
    """Create and configure Spark session"""
    return SparkSession.builder \
        .appName("ECommerceETL") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.5.0.jar") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def log_step(step_name, start_time=None):
    """Log ETL step"""
    if start_time:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"✓ {step_name} completed in {duration:.2f} seconds")
    else:
        print(f"\n{'='*60}")
        print(f"Starting: {step_name}")
        print(f"{'='*60}")
        return datetime.now()

def extract_data(spark):
    """Extract data from CSV files"""
    start = log_step("Data Extraction")
    
    try:
        # Read customers
        customers = spark.read.csv(
            f"{RAW_DATA_DIR}/customers.csv",
            header=True,
            inferSchema=True
        )
        
        # Read products
        products = spark.read.csv(
            f"{RAW_DATA_DIR}/products.csv",
            header=True,
            inferSchema=True
        )
        
        # Read orders
        orders = spark.read.csv(
            f"{RAW_DATA_DIR}/orders.csv",
            header=True,
            inferSchema=True
        )
        
        # Read order items
        order_items = spark.read.csv(
            f"{RAW_DATA_DIR}/order_items.csv",
            header=True,
            inferSchema=True
        )
        
        # Read reviews
        reviews = spark.read.csv(
            f"{RAW_DATA_DIR}/reviews.csv",
            header=True,
            inferSchema=True
        )
        
        print(f"  • Customers: {customers.count()} rows")
        print(f"  • Products: {products.count()} rows")
        print(f"  • Orders: {orders.count()} rows")
        print(f"  • Order Items: {order_items.count()} rows")
        print(f"  • Reviews: {reviews.count()} rows")
        
        log_step("Data Extraction", start)
        
        return customers, products, orders, order_items, reviews
        
    except Exception as e:
        print(f"❌ Error during data extraction: {e}")
        raise

def clean_and_transform_data(customers, products, orders, order_items, reviews):
    """Clean and transform data"""
    start = log_step("Data Cleaning & Transformation")
    
    try:
        # 1. Remove duplicates
        customers = customers.dropDuplicates(['customer_id'])
        products = products.dropDuplicates(['product_id'])
        orders = orders.dropDuplicates(['order_id'])
        
        # 2. Handle missing values
        orders = orders.fillna({'delivery_date': None, 'status': 'unknown'})
        products = products.fillna({'stock_quantity': 0})
        
        # 3. Convert date columns
        orders = orders.withColumn('order_date', to_timestamp('order_date'))
        orders = orders.withColumn('order_date_only', to_date('order_date'))
        customers = customers.withColumn('signup_date', to_date('signup_date'))
        
        # 4. Calculate derived fields
        order_items = order_items.withColumn(
            'item_total',
            (col('price') - col('discount')) * col('quantity')
        )
        
        log_step("Data Cleaning & Transformation", start)
        
        return customers, products, orders, order_items, reviews
        
    except Exception as e:
        print(f"❌ Error during transformation: {e}")
        raise

def create_sales_summary(orders):
    """Create daily sales summary"""
    start = log_step("Creating Sales Summary")
    
    try:
        sales_summary = orders.filter(col('status') == 'delivered') \
            .groupBy('order_date_only') \
            .agg(
                count('order_id').alias('total_orders'),
                sum('total_amount').alias('total_revenue'),
                avg('total_amount').alias('avg_order_value'),
                countDistinct('customer_id').alias('unique_customers'),
                sum(lit(1)).alias('total_items_sold')  # Simplified
            ) \
            .withColumnRenamed('order_date_only', 'date') \
            .orderBy('date')
        
        print(f"  • Created {sales_summary.count()} daily summaries")
        log_step("Creating Sales Summary", start)
        
        return sales_summary
        
    except Exception as e:
        print(f"❌ Error creating sales summary: {e}")
        raise

def create_product_metrics(products, order_items, orders, reviews):
    """Create product performance metrics"""
    start = log_step("Creating Product Metrics")
    
    try:
        # Join order items with orders to get delivered items
        delivered_items = order_items.join(
            orders.filter(col('status') == 'delivered'),
            'order_id'
        )
        
        # Aggregate product metrics
        product_sales = delivered_items.groupBy('product_id') \
            .agg(
                sum('item_total').alias('total_revenue'),
                sum('quantity').alias('units_sold'),
                count('order_id').alias('total_orders'),
                avg('discount').alias('avg_discount_rate'),
                max('order_date_only').alias('last_sold_date')
            )
        
        # Calculate return rate (simplified - using cancelled/returned orders)
        returned_items = order_items.join(
            orders.filter(col('status').isin(['cancelled', 'returned'])),
            'order_id'
        )
        
        return_metrics = returned_items.groupBy('product_id') \
            .agg(sum('quantity').alias('returned_quantity'))
        
        # Aggregate reviews
        review_metrics = reviews.groupBy('order_id') \
            .agg(
                avg('rating').alias('avg_rating'),
                count('review_id').alias('review_count')
            )
        
        # Join with order_items to get product_id
        review_by_product = order_items.join(review_metrics, 'order_id') \
            .groupBy('product_id') \
            .agg(
                avg('avg_rating').alias('avg_rating'),
                sum('review_count').alias('review_count')
            )
        
        # Combine everything
        product_metrics = products \
            .join(product_sales, 'product_id', 'left') \
            .join(review_by_product, 'product_id', 'left') \
            .join(return_metrics, 'product_id', 'left') \
            .select(
                'product_id',
                col('product_name').alias('product_name'),
                'category',
                'subcategory',
                col('price').alias('current_price'),
                coalesce('total_revenue', lit(0)).alias('total_revenue'),
                coalesce('units_sold', lit(0)).cast('int').alias('units_sold'),
                coalesce('total_orders', lit(0)).cast('int').alias('total_orders'),
                round(coalesce('avg_rating', lit(0)), 2).alias('avg_rating'),
                coalesce('review_count', lit(0)).cast('int').alias('review_count'),
                'stock_quantity',
                round(
                    coalesce('returned_quantity', lit(0)) / 
                    (coalesce('units_sold', lit(1)) + coalesce('returned_quantity', lit(0))),
                    4
                ).alias('return_rate'),
                round(coalesce('avg_discount_rate', lit(0)), 4).alias('avg_discount_rate'),
                'last_sold_date'
            )
        
        print(f"  • Created metrics for {product_metrics.count()} products")
        log_step("Creating Product Metrics", start)
        
        return product_metrics
        
    except Exception as e:
        print(f"❌ Error creating product metrics: {e}")
        raise

def create_customer_segments(customers, orders):
    """Create customer segmentation"""
    start = log_step("Creating Customer Segments")
    
    try:
        # Calculate customer metrics
        customer_metrics = orders.filter(col('status') == 'delivered') \
            .groupBy('customer_id') \
            .agg(
                count('order_id').alias('total_orders'),
                sum('total_amount').alias('lifetime_value'),
                avg('total_amount').alias('avg_order_value'),
                min('order_date_only').alias('first_order_date'),
                max('order_date_only').alias('last_order_date')
            )
        
        # Add days since last order
        customer_metrics = customer_metrics.withColumn(
            'days_since_last_order',
            datediff(current_date(), col('last_order_date'))
        )
        
        # Segment customers based on lifetime value
        customer_segments = customer_metrics.withColumn(
            'segment',
            when(col('lifetime_value') >= 1000, 'High Value')
            .when(col('lifetime_value') >= 500, 'Medium Value')
            .otherwise('Low Value')
        )
        
        # Join with customer details
        customer_segments = customers.join(customer_segments, 'customer_id', 'left') \
            .select(
                'customer_id',
                col('name').alias('customer_name'),
                coalesce('segment', lit('Low Value')).alias('segment'),
                coalesce('total_orders', lit(0)).cast('int').alias('total_orders'),
                coalesce('lifetime_value', lit(0)).alias('lifetime_value'),
                'avg_order_value',
                'first_order_date',
                'last_order_date',
                'days_since_last_order',
                lit(0).alias('total_items_purchased'),  # Simplified
                lit(None).cast('string').alias('favorite_category'),  # Simplified
                'city',
                'state',
                'signup_date',
                when(coalesce('days_since_last_order', lit(999)) <= 90, True)
                .otherwise(False).alias('is_active')
            )
        
        print(f"  • Segmented {customer_segments.count()} customers")
        log_step("Creating Customer Segments", start)
        
        return customer_segments
        
    except Exception as e:
        print(f"❌ Error creating customer segments: {e}")
        raise

def create_category_performance(products, order_items, orders):
    """Create category performance metrics"""
    start = log_step("Creating Category Performance")
    
    try:
        # Join items with delivered orders and products
        category_sales = order_items \
            .join(orders.filter(col('status') == 'delivered'), 'order_id') \
            .join(products, 'product_id') \
            .groupBy('category') \
            .agg(
                sum('item_total').alias('total_revenue'),
                count('order_id').alias('total_orders'),
                countDistinct('product_id').alias('unique_products'),
                sum('quantity').alias('units_sold'),
                avg(col('price')).alias('avg_price')
            )
        
        print(f"  • Created metrics for {category_sales.count()} categories")
        log_step("Creating Category Performance", start)
        
        return category_sales
        
    except Exception as e:
        print(f"❌ Error creating category performance: {e}")
        raise

def create_monthly_trends(orders):
    """Create monthly trends"""
    start = log_step("Creating Monthly Trends")
    
    try:
        monthly = orders.filter(col('status') == 'delivered') \
            .withColumn('year_month', date_format('order_date', 'yyyy-MM')) \
            .groupBy('year_month') \
            .agg(
                sum('total_amount').alias('total_revenue'),
                count('order_id').alias('total_orders'),
                countDistinct('customer_id').alias('unique_customers'),
                avg('total_amount').alias('avg_order_value')
            ) \
            .orderBy('year_month')
        
        print(f"  • Created {monthly.count()} monthly summaries")
        log_step("Creating Monthly Trends", start)
        
        return monthly
        
    except Exception as e:
        print(f"❌ Error creating monthly trends: {e}")
        raise

def create_geographic_performance(customers, orders):
    """Create geographic performance metrics"""
    start = log_step("Creating Geographic Performance")
    
    try:
        geo_metrics = orders.filter(col('status') == 'delivered') \
            .join(customers, 'customer_id') \
            .groupBy('state') \
            .agg(
                countDistinct('customer_id').alias('total_customers'),
                count('order_id').alias('total_orders'),
                sum('total_amount').alias('total_revenue'),
                avg('total_amount').alias('avg_order_value')
            )
        
        print(f"  • Created metrics for {geo_metrics.count()} states")
        log_step("Creating Geographic Performance", start)
        
        return geo_metrics
        
    except Exception as e:
        print(f"❌ Error creating geographic performance: {e}")
        raise

def save_to_postgres(df, table_name, mode='overwrite'):
    """Save DataFrame to PostgreSQL"""
    try:
        df.write \
            .jdbc(
                url=JDBC_URL,
                table=f"analytics.{table_name}",
                mode=mode,
                properties=JDBC_PROPERTIES
            )
        print(f"  ✓ Saved to analytics.{table_name}")
    except Exception as e:
        print(f"  ❌ Error saving to {table_name}: {e}")
        raise

def save_to_parquet(df, file_name):
    """Save DataFrame to Parquet"""
    try:
        output_path = f"{PROCESSED_DATA_DIR}/{file_name}"
        df.write.mode('overwrite').parquet(output_path)
        print(f"  ✓ Saved to {output_path}")
    except Exception as e:
        print(f"  ❌ Error saving parquet {file_name}: {e}")
        raise

def main():
    """Main ETL pipeline"""
    print("\n" + "="*60)
    print("E-COMMERCE ANALYTICS ETL PIPELINE")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    overall_start = datetime.now()
    
    try:
        # Create Spark session
        spark = create_spark_session()
        spark.sparkContext.setLogLevel("WARN")
        
        # Extract
        customers, products, orders, order_items, reviews = extract_data(spark)
        
        # Transform
        customers, products, orders, order_items, reviews = clean_and_transform_data(
            customers, products, orders, order_items, reviews
        )
        
        # Create analytical tables
        sales_summary = create_sales_summary(orders)
        product_metrics = create_product_metrics(products, order_items, orders, reviews)
        customer_segments = create_customer_segments(customers, orders)
        category_performance = create_category_performance(products, order_items, orders)
        monthly_trends = create_monthly_trends(orders)
        geographic_performance = create_geographic_performance(customers, orders)
        
        # Load to PostgreSQL
        start = log_step("Loading to PostgreSQL")
        save_to_postgres(sales_summary, 'sales_summary')
        save_to_postgres(product_metrics, 'product_metrics')
        save_to_postgres(customer_segments, 'customer_segments')
        save_to_postgres(category_performance, 'category_performance')
        save_to_postgres(monthly_trends, 'monthly_trends')
        save_to_postgres(geographic_performance, 'geographic_performance')
        log_step("Loading to PostgreSQL", start)
        
        # Save to Parquet
        start = log_step("Saving to Parquet")
        save_to_parquet(sales_summary, 'sales_summary.parquet')
        save_to_parquet(product_metrics, 'product_metrics.parquet')
        save_to_parquet(customer_segments, 'customer_segments.parquet')
        log_step("Saving to Parquet", start)
        
        # Update data quality metrics
        # (Implementation would go here)
        
        # Log success
        duration = (datetime.now() - overall_start).total_seconds()
        print("\n" + "="*60)
        print("✅ ETL PIPELINE COMPLETED SUCCESSFULLY")
        print(f"Total Duration: {duration:.2f} seconds")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        spark.stop()
        sys.exit(0)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ ETL PIPELINE FAILED: {e}")
        print("="*60 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
