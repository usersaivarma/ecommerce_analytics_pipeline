-- Database initialization script for E-Commerce Analytics

-- Create schema for processed data
CREATE SCHEMA IF NOT EXISTS analytics;

-- ============================================
-- Sales Summary Table
-- ============================================
CREATE TABLE IF NOT EXISTS analytics.sales_summary (
    date DATE PRIMARY KEY,
    total_orders INTEGER NOT NULL,
    total_revenue DECIMAL(12, 2) NOT NULL,
    avg_order_value DECIMAL(10, 2) NOT NULL,
    unique_customers INTEGER NOT NULL,
    total_items_sold INTEGER NOT NULL,
    avg_items_per_order DECIMAL(5, 2),
    cancelled_orders INTEGER DEFAULT 0,
    returned_orders INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for date range queries
CREATE INDEX idx_sales_summary_date ON analytics.sales_summary(date);

-- ============================================
-- Product Metrics Table
-- ============================================
CREATE TABLE IF NOT EXISTS analytics.product_metrics (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    current_price DECIMAL(10, 2),
    total_revenue DECIMAL(12, 2) NOT NULL DEFAULT 0,
    units_sold INTEGER NOT NULL DEFAULT 0,
    total_orders INTEGER NOT NULL DEFAULT 0,
    avg_rating DECIMAL(3, 2),
    review_count INTEGER DEFAULT 0,
    stock_quantity INTEGER,
    return_rate DECIMAL(5, 4) DEFAULT 0,
    avg_discount_rate DECIMAL(5, 4) DEFAULT 0,
    last_sold_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_product_metrics_category ON analytics.product_metrics(category);
CREATE INDEX idx_product_metrics_revenue ON analytics.product_metrics(total_revenue DESC);
CREATE INDEX idx_product_metrics_units_sold ON analytics.product_metrics(units_sold DESC);
CREATE INDEX idx_product_metrics_rating ON analytics.product_metrics(avg_rating DESC);

-- ============================================
-- Customer Segments Table
-- ============================================
CREATE TABLE IF NOT EXISTS analytics.customer_segments (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(200),
    segment VARCHAR(20) NOT NULL,
    total_orders INTEGER NOT NULL DEFAULT 0,
    lifetime_value DECIMAL(12, 2) NOT NULL DEFAULT 0,
    avg_order_value DECIMAL(10, 2),
    first_order_date DATE,
    last_order_date DATE,
    days_since_last_order INTEGER,
    total_items_purchased INTEGER DEFAULT 0,
    favorite_category VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    signup_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for segmentation queries
CREATE INDEX idx_customer_segments_segment ON analytics.customer_segments(segment);
CREATE INDEX idx_customer_segments_ltv ON analytics.customer_segments(lifetime_value DESC);
CREATE INDEX idx_customer_segments_state ON analytics.customer_segments(state);

-- ============================================
-- Category Performance Table
-- ============================================
CREATE TABLE IF NOT EXISTS analytics.category_performance (
    category VARCHAR(100) PRIMARY KEY,
    total_revenue DECIMAL(12, 2) NOT NULL DEFAULT 0,
    total_orders INTEGER NOT NULL DEFAULT 0,
    unique_products INTEGER NOT NULL DEFAULT 0,
    units_sold INTEGER NOT NULL DEFAULT 0,
    avg_price DECIMAL(10, 2),
    avg_rating DECIMAL(3, 2),
    total_reviews INTEGER DEFAULT 0,
    return_rate DECIMAL(5, 4) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_category_performance_revenue ON analytics.category_performance(total_revenue DESC);

-- ============================================
-- Monthly Trends Table
-- ============================================
CREATE TABLE IF NOT EXISTS analytics.monthly_trends (
    year_month VARCHAR(7) PRIMARY KEY,  -- Format: 'YYYY-MM'
    total_revenue DECIMAL(12, 2) NOT NULL,
    total_orders INTEGER NOT NULL,
    unique_customers INTEGER NOT NULL,
    avg_order_value DECIMAL(10, 2),
    new_customers INTEGER DEFAULT 0,
    returning_customers INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Order Status Summary Table
-- ============================================
CREATE TABLE IF NOT EXISTS analytics.order_status_summary (
    status VARCHAR(50) PRIMARY KEY,
    order_count INTEGER NOT NULL DEFAULT 0,
    total_value DECIMAL(12, 2) NOT NULL DEFAULT 0,
    percentage DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Geographic Performance Table
-- ============================================
CREATE TABLE IF NOT EXISTS analytics.geographic_performance (
    state VARCHAR(100) PRIMARY KEY,
    total_customers INTEGER NOT NULL DEFAULT 0,
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_revenue DECIMAL(12, 2) NOT NULL DEFAULT 0,
    avg_order_value DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_geographic_performance_revenue ON analytics.geographic_performance(total_revenue DESC);

-- ============================================
-- Data Quality Metrics Table
-- ============================================
CREATE TABLE IF NOT EXISTS analytics.data_quality_metrics (
    metric_name VARCHAR(100) PRIMARY KEY,
    metric_value VARCHAR(500),
    status VARCHAR(20),  -- 'PASS' or 'FAIL'
    last_check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- ============================================
-- ETL Run History Table
-- ============================================
CREATE TABLE IF NOT EXISTS analytics.etl_run_history (
    run_id SERIAL PRIMARY KEY,
    run_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,  -- 'SUCCESS', 'FAILED', 'RUNNING'
    records_processed INTEGER,
    duration_seconds INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_etl_run_history_date ON analytics.etl_run_history(run_date DESC);

-- ============================================
-- Views for Common Queries
-- ============================================

-- Top performing products
CREATE OR REPLACE VIEW analytics.top_products AS
SELECT 
    product_id,
    product_name,
    category,
    total_revenue,
    units_sold,
    avg_rating,
    review_count,
    RANK() OVER (ORDER BY total_revenue DESC) as revenue_rank,
    RANK() OVER (ORDER BY units_sold DESC) as units_rank
FROM analytics.product_metrics
WHERE units_sold > 0
ORDER BY total_revenue DESC
LIMIT 100;

-- Customer value tiers
CREATE OR REPLACE VIEW analytics.customer_value_tiers AS
SELECT 
    segment,
    COUNT(*) as customer_count,
    AVG(lifetime_value) as avg_lifetime_value,
    SUM(lifetime_value) as total_value,
    AVG(total_orders) as avg_orders,
    AVG(days_since_last_order) as avg_days_since_last_order
FROM analytics.customer_segments
GROUP BY segment
ORDER BY avg_lifetime_value DESC;

-- Recent sales performance
CREATE OR REPLACE VIEW analytics.recent_sales_performance AS
SELECT 
    date,
    total_revenue,
    total_orders,
    avg_order_value,
    unique_customers,
    total_revenue - LAG(total_revenue) OVER (ORDER BY date) as revenue_change,
    total_orders - LAG(total_orders) OVER (ORDER BY date) as orders_change
FROM analytics.sales_summary
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;

-- ============================================
-- Grant Permissions
-- ============================================
GRANT USAGE ON SCHEMA analytics TO user_sai_varma;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA analytics TO user_sai_varma;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO user_sai_varma;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA analytics TO user_sai_varma;

-- ============================================
-- Sample Data Quality Checks
-- ============================================
INSERT INTO analytics.data_quality_metrics (metric_name, metric_value, status, description) VALUES
('last_etl_run', 'Not run yet', 'PENDING', 'Timestamp of last successful ETL run'),
('total_records_processed', '0', 'PENDING', 'Total records processed in last ETL run'),
('data_freshness_hours', 'N/A', 'PENDING', 'Hours since last data update')
ON CONFLICT (metric_name) DO NOTHING;

-- ============================================
-- Completion Message
-- ============================================
DO $$
BEGIN
    RAISE NOTICE 'Database initialization complete!';
    RAISE NOTICE 'Schema "analytics" created with all tables and views.';
END $$;
