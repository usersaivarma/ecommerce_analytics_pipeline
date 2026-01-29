# E-Commerce Analytics Pipeline - Project Architecture

## Project Overview
Build a complete data pipeline that ingests raw e-commerce data, processes it with PySpark, and serves insights through containerized web applications.

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  Raw Data (CSV/JSON)                                         │
│  ├── orders.csv                                              │
│  ├── customers.csv                                           │
│  ├── products.csv                                            │
│  └── reviews.csv                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   ETL LAYER (PySpark)                        │
├─────────────────────────────────────────────────────────────┤
│  Container: pyspark-etl                                      │
│  ├── Data Validation                                         │
│  ├── Cleaning & Transformation                              │
│  ├── Feature Engineering                                     │
│  ├── Aggregations                                            │
│  └── Output: Parquet files + PostgreSQL                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  PROCESSED DATA STORE                        │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL Container: postgres-db                           │
│  ├── sales_summary                                           │
│  ├── product_metrics                                         │
│  ├── customer_segments                                       │
│  └── daily_aggregates                                        │
│                                                              │
│  + Parquet Files: /data/processed/                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                    ↓
┌──────────────────────┐          ┌──────────────────────┐
│   API LAYER          │          │  DASHBOARD LAYER     │
│   (FastAPI)          │          │  (Streamlit)         │
├──────────────────────┤          ├──────────────────────┤
│ Container: api       │          │ Container: dashboard │
│                      │          │                      │
│ Endpoints:           │          │ Pages:               │
│ - GET /health        │          │ - Home               │
│ - GET /sales/summary │          │ - Sales Analytics    │
│ - GET /products/top  │          │ - Product Performance│
│ - GET /customers/... │          │ - Customer Insights  │
│ - POST /query        │          │ - Data Quality       │
│                      │          │                      │
│ Port: 8000           │          │ Port: 8501           │
└──────────────────────┘          └──────────────────────┘
```

---

## Project Structure

```
ecommerce-analytics/
├── README.md
├── docker-compose.yml
├── Makefile
├── .env.example
├── requirements.txt
│
├── data/
│   ├── raw/                    # Raw CSV files
│   ├── processed/              # Parquet outputs
│   └── sample_data/            # Small datasets for testing
│
├── etl/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── spark_jobs/
│   │   ├── __init__.py
│   │   ├── extract.py          # Data loading
│   │   ├── transform.py        # Transformations
│   │   ├── load.py             # Save to DB/files
│   │   └── main.py             # Orchestrator
│   ├── config/
│   │   └── spark_config.py
│   └── utils/
│       ├── data_quality.py
│       └── logger.py
│
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # FastAPI app
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── sales.py
│   │   ├── products.py
│   │   └── customers.py
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── database/
│   │   └── connection.py
│   └── tests/
│       └── test_api.py
│
├── dashboard/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                  # Main Streamlit app
│   ├── pages/
│   │   ├── 1_Sales_Analytics.py
│   │   ├── 2_Product_Performance.py
│   │   └── 3_Customer_Insights.py
│   ├── components/
│   │   ├── charts.py
│   │   └── metrics.py
│   └── utils/
│       └── api_client.py       # Calls FastAPI
│
├── flask_app/                  # Optional: Flask alternative
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
│
├── database/
│   ├── init.sql                # Database schema
│   └── seed.sql                # Sample data
│
└── docs/
    ├── architecture.md
    ├── api_docs.md
    └── deployment_comparison.md  # Serverless vs Serverfull
```

---

## Implementation Phases

### Phase 1: Data Setup & PySpark ETL (Week 1)
**Tasks:**
1. Download/generate datasets
2. Set up PySpark locally (can use local mode)
3. Build ETL pipeline:
   - Extract: Read CSV files
   - Transform:
     * Clean missing values
     * Join orders with customers and products
     * Calculate metrics (order value, customer lifetime value)
     * Create time-based features (day of week, month, quarter)
     * Aggregate data for dashboards
   - Load: Save to Parquet and PostgreSQL

**Key PySpark Operations:**
```python
# Data Quality Checks
- Check for nulls
- Validate data types
- Check for duplicates
- Range validation (dates, amounts)

# Transformations
- window functions for running totals
- groupBy for aggregations
- join operations
- withColumn for feature engineering

# Sample transformations:
- Customer segments (high/medium/low value)
- Product performance metrics
- Sales trends by time period
- Geographic analysis
```

**Deliverable:** Working PySpark pipeline that processes raw data and outputs clean, aggregated data

---

### Phase 2: PostgreSQL & Docker Setup (Week 1-2)
**Tasks:**
1. Create PostgreSQL container
2. Design database schema for processed data
3. Write init scripts
4. Test data loading from PySpark
5. Create indexes for query performance

**Database Tables:**
```sql
-- sales_summary
CREATE TABLE sales_summary (
    date DATE PRIMARY KEY,
    total_orders INT,
    total_revenue DECIMAL(10,2),
    avg_order_value DECIMAL(10,2),
    unique_customers INT
);

-- product_metrics
CREATE TABLE product_metrics (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(100),
    total_sales DECIMAL(10,2),
    units_sold INT,
    avg_rating DECIMAL(3,2),
    review_count INT
);

-- customer_segments
CREATE TABLE customer_segments (
    customer_id VARCHAR(50) PRIMARY KEY,
    segment VARCHAR(20),
    total_orders INT,
    lifetime_value DECIMAL(10,2),
    first_order_date DATE,
    last_order_date DATE
);
```

**Deliverable:** Dockerized PostgreSQL with schema and sample data

---

### Phase 3: FastAPI Development (Week 2)
**Tasks:**
1. Create FastAPI application
2. Implement database connection pooling
3. Build REST endpoints
4. Add request/response validation (Pydantic)
5. Write basic tests
6. Dockerize the API

**API Endpoints:**
```
GET  /                          # Health check
GET  /sales/summary             # Overall sales metrics
GET  /sales/daily?start=&end=   # Daily sales data
GET  /products/top?limit=10     # Top products
GET  /products/{id}             # Product details
GET  /customers/segments        # Customer segmentation
GET  /customers/{id}/orders     # Customer order history
POST /query                     # Custom SQL queries (controlled)
```

**Features to Implement:**
- Query parameter validation
- Error handling
- CORS configuration
- API documentation (auto-generated by FastAPI)
- Optional: Basic authentication
- Optional: Rate limiting

**Deliverable:** Dockerized FastAPI service with working endpoints

---

### Phase 4: Streamlit Dashboard (Week 2-3)
**Tasks:**
1. Create multi-page Streamlit app
2. Connect to FastAPI backend
3. Build interactive visualizations
4. Add filters and controls
5. Dockerize the dashboard

**Dashboard Pages:**

**Page 1: Sales Overview**
- KPI cards (total revenue, orders, avg order value)
- Line chart: sales over time
- Bar chart: top categories
- Geographic map (if data available)

**Page 2: Product Performance**
- Product ranking table
- Category comparison
- Stock levels
- Rating distribution

**Page 3: Customer Insights**
- Customer segments pie chart
- Cohort analysis
- Customer lifetime value distribution
- Retention metrics

**Page 4: Data Quality**
- Show data freshness
- Record counts
- Quality check results
- ETL pipeline status

**Deliverable:** Interactive Streamlit dashboard calling FastAPI

---

### Phase 5: Docker Compose & Orchestration (Week 3)
**Tasks:**
1. Create docker-compose.yml
2. Configure networking between containers
3. Set up volumes for data persistence
4. Add environment variables
5. Create Makefile for easy commands

**docker-compose.yml structure:**
```yaml
services:
  postgres:
    # Database service
  
  etl:
    # PySpark ETL job
    depends_on: [postgres]
  
  api:
    # FastAPI service
    depends_on: [postgres]
  
  dashboard:
    # Streamlit app
    depends_on: [api]
```

**Makefile commands:**
```makefile
make setup      # Initial setup
make run-etl    # Run ETL pipeline
make start      # Start all services
make stop       # Stop all services
make logs       # View logs
make test       # Run tests
make clean      # Clean up
```

**Deliverable:** Complete orchestrated system running with one command

---

### Phase 6: Optional Enhancements (Week 4)
1. **Flask Alternative**: Build a simple Flask API for comparison
2. **Databricks**: Run your PySpark code on Databricks Community Edition
3. **Data Quality Framework**: Implement Great Expectations
4. **CI/CD**: Add GitHub Actions for testing
5. **Monitoring**: Add basic logging and metrics
6. **Documentation**: Create comprehensive README and deployment guide

---

## Key Learning Outcomes

### PySpark ETL
- Reading various file formats
- Data validation and quality checks
- Complex transformations and aggregations
- Writing to multiple targets
- Performance optimization

### Containerization
- Dockerfile best practices
- Multi-container orchestration
- Volume management
- Networking between containers
- Environment configuration

### API Development
- RESTful API design
- Request validation
- Database connection handling
- Error handling
- API documentation

### Dashboard Development
- Interactive visualizations
- State management
- API integration
- User experience design

### Deployment Concepts
- Local simulation of production environment
- Serverless vs Serverfull discussion
- Scalability considerations
- Monitoring and logging

---

## Technologies & Tools

**Required:**
- Python 3.9+
- PySpark 3.4+
- FastAPI
- Streamlit
- PostgreSQL
- Docker & Docker Compose

**Python Libraries:**
```
# ETL
pyspark==3.4.0
pandas==2.0.0
faker==19.0.0  # for synthetic data

# API
fastapi==0.104.0
uvicorn==0.24.0
sqlalchemy==2.0.0
psycopg2-binary==2.9.9
pydantic==2.5.0

# Dashboard
streamlit==1.28.0
plotly==5.17.0
requests==2.31.0

# Testing
pytest==7.4.0
httpx==0.25.0  # for FastAPI testing
```

---

## Deployment Discussion

Create a document comparing deployment strategies:

### Serverfull Deployment
- Traditional VMs or containers on EC2/GCE
- Always running
- Predictable costs
- Full control
- Examples: API on EC2 + RDS

### Serverless Deployment
- Functions as a Service (Lambda, Cloud Functions)
- Pay per execution
- Auto-scaling
- Less operational overhead
- Examples: FastAPI on AWS Lambda + API Gateway

**Your Implementation**: Discuss how your Docker setup could be deployed to both architectures

---

## Success Metrics

- [ ] ETL pipeline processes data successfully
- [ ] All data quality checks pass
- [ ] API returns correct data for all endpoints
- [ ] Dashboard visualizations are interactive and accurate
- [ ] All services run together with docker-compose
- [ ] Documentation is complete
- [ ] Project is on GitHub with good README

---

## Timeline

**Week 1**: Data setup + PySpark ETL + PostgreSQL
**Week 2**: FastAPI + Start Streamlit
**Week 3**: Complete Streamlit + Docker Compose + Integration
**Week 4**: Polish, documentation, optional enhancements

Total: 3-4 weeks for complete project

---

## Next Steps

1. Set up project directory structure
2. Choose your dataset
3. Start with PySpark ETL pipeline
4. Build incrementally, testing each component
5. Integrate everything with Docker Compose
6. Document your learnings

Would you like me to create starter code for any specific component?
