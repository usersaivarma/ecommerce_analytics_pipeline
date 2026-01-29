"""
FastAPI application for E-Commerce Analytics
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import date, datetime
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ecommerce_analytics")
POSTGRES_USER = os.getenv("POSTGRES_USER", "ecommerce_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ecommerce_pass")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create database engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="E-Commerce Analytics API",
    description="REST API for e-commerce analytics data",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Database dependency
# ============================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# Health Check
# ============================================
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "E-Commerce Analytics API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check including database connection"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# Sales Endpoints
# ============================================
@app.get("/sales/summary")
async def get_sales_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get overall sales summary with optional date filtering"""
    try:
        db = SessionLocal()
        
        query = """
            SELECT 
                COUNT(*) as total_days,
                SUM(total_orders) as total_orders,
                SUM(total_revenue) as total_revenue,
                AVG(avg_order_value) as avg_order_value,
                SUM(total_items_sold) as total_items_sold,
                MAX(date) as latest_date
            FROM analytics.sales_summary
            WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        
        result = db.execute(text(query), params).fetchone()
        db.close()
        
        if result:
            return {
                "total_days": result[0] or 0,
                "total_orders": result[1] or 0,
                "total_revenue": float(result[2] or 0),
                "avg_order_value": float(result[3] or 0),
                "total_items_sold": result[4] or 0,
                "latest_date": str(result[5]) if result[5] else None
            }
        else:
            return {"message": "No data available"}
            
    except Exception as e:
        logger.error(f"Error in get_sales_summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/daily")
async def get_daily_sales(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(30, ge=1, le=365)
):
    """Get daily sales data"""
    try:
        db = SessionLocal()
        
        query = """
            SELECT 
                date,
                total_orders,
                total_revenue,
                avg_order_value,
                unique_customers,
                total_items_sold
            FROM analytics.sales_summary
            WHERE 1=1
        """
        
        params = {'limit': limit}
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        
        query += " ORDER BY date DESC LIMIT :limit"
        
        results = db.execute(text(query), params).fetchall()
        db.close()
        
        return {
            "count": len(results),
            "data": [
                {
                    "date": str(row[0]),
                    "total_orders": row[1],
                    "total_revenue": float(row[2]),
                    "avg_order_value": float(row[3]),
                    "unique_customers": row[4],
                    "total_items_sold": row[5]
                }
                for row in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in get_daily_sales: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sales/monthly")
async def get_monthly_trends():
    """Get monthly sales trends"""
    try:
        db = SessionLocal()
        
        query = """
            SELECT 
                year_month,
                total_revenue,
                total_orders,
                unique_customers,
                avg_order_value,
                new_customers,
                returning_customers
            FROM analytics.monthly_trends
            ORDER BY year_month DESC
            LIMIT 12
        """
        
        results = db.execute(text(query)).fetchall()
        db.close()
        
        return {
            "count": len(results),
            "data": [
                {
                    "year_month": row[0],
                    "total_revenue": float(row[1]),
                    "total_orders": row[2],
                    "unique_customers": row[3],
                    "avg_order_value": float(row[4]),
                    "new_customers": row[5],
                    "returning_customers": row[6]
                }
                for row in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in get_monthly_trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Product Endpoints
# ============================================
@app.get("/products/top")
async def get_top_products(
    metric: str = Query("revenue", regex="^(revenue|units|rating)$"),
    limit: int = Query(10, ge=1, le=100)
):
    """Get top products by revenue, units sold, or rating"""
    try:
        db = SessionLocal()
        
        order_by = {
            "revenue": "total_revenue DESC",
            "units": "units_sold DESC",
            "rating": "avg_rating DESC"
        }[metric]
        
        query = f"""
            SELECT 
                product_id,
                product_name,
                category,
                subcategory,
                total_revenue,
                units_sold,
                avg_rating,
                review_count,
                current_price
            FROM analytics.product_metrics
            WHERE units_sold > 0
            ORDER BY {order_by}
            LIMIT :limit
        """
        
        results = db.execute(text(query), {'limit': limit}).fetchall()
        db.close()
        
        return {
            "metric": metric,
            "count": len(results),
            "data": [
                {
                    "product_id": row[0],
                    "product_name": row[1],
                    "category": row[2],
                    "subcategory": row[3],
                    "total_revenue": float(row[4]),
                    "units_sold": row[5],
                    "avg_rating": float(row[6]) if row[6] else None,
                    "review_count": row[7],
                    "current_price": float(row[8]) if row[8] else None
                }
                for row in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in get_top_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/categories")
async def get_category_performance():
    """Get performance metrics by category"""
    try:
        db = SessionLocal()
        
        query = """
            SELECT 
                category,
                total_revenue,
                total_orders,
                unique_products,
                units_sold,
                avg_price,
                avg_rating,
                total_reviews
            FROM analytics.category_performance
            ORDER BY total_revenue DESC
        """
        
        results = db.execute(text(query)).fetchall()
        db.close()
        
        return {
            "count": len(results),
            "data": [
                {
                    "category": row[0],
                    "total_revenue": float(row[1]),
                    "total_orders": row[2],
                    "unique_products": row[3],
                    "units_sold": row[4],
                    "avg_price": float(row[5]) if row[5] else None,
                    "avg_rating": float(row[6]) if row[6] else None,
                    "total_reviews": row[7]
                }
                for row in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in get_category_performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
async def get_product_details(product_id: str):
    """Get detailed metrics for a specific product"""
    try:
        db = SessionLocal()
        
        query = """
            SELECT 
                product_id,
                product_name,
                category,
                subcategory,
                current_price,
                total_revenue,
                units_sold,
                total_orders,
                avg_rating,
                review_count,
                stock_quantity,
                return_rate,
                avg_discount_rate,
                last_sold_date
            FROM analytics.product_metrics
            WHERE product_id = :product_id
        """
        
        result = db.execute(text(query), {'product_id': product_id}).fetchone()
        db.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "product_id": result[0],
            "product_name": result[1],
            "category": result[2],
            "subcategory": result[3],
            "current_price": float(result[4]) if result[4] else None,
            "total_revenue": float(result[5]),
            "units_sold": result[6],
            "total_orders": result[7],
            "avg_rating": float(result[8]) if result[8] else None,
            "review_count": result[9],
            "stock_quantity": result[10],
            "return_rate": float(result[11]) if result[11] else 0,
            "avg_discount_rate": float(result[12]) if result[12] else 0,
            "last_sold_date": str(result[13]) if result[13] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_product_details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# ============================================
# Customer Endpoints
# ============================================
@app.get("/customers/segments")
async def get_customer_segments():
    """Get customer segmentation summary"""
    try:
        db = SessionLocal()
        
        query = """
            SELECT * FROM analytics.customer_value_tiers
            ORDER BY avg_lifetime_value DESC
        """
        
        results = db.execute(text(query)).fetchall()
        db.close()
        
        return {
            "count": len(results),
            "data": [
                {
                    "segment": row[0],
                    "customer_count": row[1],
                    "avg_lifetime_value": float(row[2]),
                    "total_value": float(row[3]),
                    "avg_orders": float(row[4]),
                    "avg_days_since_last_order": float(row[5]) if row[5] else None
                }
                for row in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in get_customer_segments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers/geographic")
async def get_geographic_performance(limit: int = Query(20, ge=1, le=100)):
    """Get sales performance by geographic location"""
    try:
        db = SessionLocal()
        
        query = """
            SELECT 
                state,
                total_customers,
                total_orders,
                total_revenue,
                avg_order_value
            FROM analytics.geographic_performance
            ORDER BY total_revenue DESC
            LIMIT :limit
        """
        
        results = db.execute(text(query), {'limit': limit}).fetchall()
        db.close()
        
        return {
            "count": len(results),
            "data": [
                {
                    "state": row[0],
                    "total_customers": row[1],
                    "total_orders": row[2],
                    "total_revenue": float(row[3]),
                    "avg_order_value": float(row[4]) if row[4] else None
                }
                for row in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in get_geographic_performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Data Quality Endpoints
# ============================================
@app.get("/data-quality/metrics")
async def get_data_quality_metrics():
    """Get data quality metrics from last ETL run"""
    try:
        db = SessionLocal()
        
        query = """
            SELECT 
                metric_name,
                metric_value,
                status,
                last_check_time,
                description
            FROM analytics.data_quality_metrics
            ORDER BY last_check_time DESC
        """
        
        results = db.execute(text(query)).fetchall()
        db.close()
        
        return {
            "count": len(results),
            "data": [
                {
                    "metric_name": row[0],
                    "metric_value": row[1],
                    "status": row[2],
                    "last_check_time": row[3].isoformat() if row[3] else None,
                    "description": row[4]
                }
                for row in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in get_data_quality_metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/etl/history")
async def get_etl_history(limit: int = Query(10, ge=1, le=50)):
    """Get ETL run history"""
    try:
        db = SessionLocal()
        
        query = """
            SELECT 
                run_id,
                run_date,
                status,
                records_processed,
                duration_seconds,
                error_message
            FROM analytics.etl_run_history
            ORDER BY run_date DESC
            LIMIT :limit
        """
        
        results = db.execute(text(query), {'limit': limit}).fetchall()
        db.close()
        
        return {
            "count": len(results),
            "data": [
                {
                    "run_id": row[0],
                    "run_date": row[1].isoformat() if row[1] else None,
                    "status": row[2],
                    "records_processed": row[3],
                    "duration_seconds": row[4],
                    "error_message": row[5]
                }
                for row in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in get_etl_history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
