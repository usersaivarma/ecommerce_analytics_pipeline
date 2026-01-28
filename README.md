# 🛒 E-Commerce Analytics Pipeline

A complete end-to-end data engineering project demonstrating ETL with PySpark, containerized applications, and interactive dashboards.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment Considerations](#deployment-considerations)
- [Troubleshooting](#troubleshooting)
- [Learning Outcomes](#learning-outcomes)

## 🎯 Overview

This project implements a production-grade analytics pipeline for e-commerce data, featuring:

- **PySpark ETL Pipeline**: Process and transform raw data into actionable insights
- **PostgreSQL Data Warehouse**: Store processed analytics data
- **FastAPI Backend**: RESTful API for data access
- **Streamlit Dashboard**: Interactive data visualization
- **Docker Orchestration**: All services containerized and orchestrated

## 🏗️ Architecture

```
┌─────────────┐
│  Raw Data   │ (CSV files)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  PySpark    │ ETL Processing
│     ETL     │ - Clean & Transform
└──────┬──────┘ - Aggregate
       │        - Quality Checks
       ↓
┌─────────────┐
│ PostgreSQL  │ Analytics Database
│  Database   │
└──────┬──────┘
       │
       ├──────────┐
       ↓          ↓
┌──────────┐  ┌──────────┐
│ FastAPI  │  │Streamlit │
│   API    │←─┤Dashboard │
└──────────┘  └──────────┘
```

## 🛠️ Technologies Used

### Core Technologies
- **Python 3.9+**: Primary programming language
- **PySpark 3.4+**: Distributed data processing
- **PostgreSQL 15**: Data warehouse
- **FastAPI**: REST API framework
- **Streamlit**: Dashboard framework
- **Docker & Docker Compose**: Containerization

### Python Libraries
- **pandas**: Data manipulation
- **sqlalchemy**: Database ORM
- **plotly**: Interactive visualizations
- **faker**: Synthetic data generation
- **pytest**: Testing framework

### Verify Installation

```bash
docker --version
docker-compose --version
python --version
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ecommerce-analytics
```

### 2. Initial Setup

```bash
# Run the setup script
make setup

# This will:
# - Create necessary directories
# - Copy .env.example to .env
```

### 3. Generate Sample Data

```bash
# Install Python dependencies for data generation
pip install pandas faker numpy

# Generate synthetic e-commerce data
make generate-data

# This creates approximately:
# - 1,000 customers
# - 200 products
# - 5,000 orders
# - Order items & reviews
```

### 4. Build and Start Services

```bash
# Build all Docker images
make build

# Start PostgreSQL and wait for it to initialize
docker-compose up -d postgres
sleep 10

# Run ETL pipeline to process data
make run-etl

# Start API and Dashboard
docker-compose up -d api dashboard
```

### 5. Access the Applications

- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### One-Command Setup (Alternative)

```bash
# Run complete setup in one command
make full-setup
```

## 📁 Project Structure

```
ecommerce-analytics/
├── README.md                   # This file
├── docker-compose.yml          # Service orchestration
├── Makefile                    # Automation commands
├── .env.example               # Environment template
│
├── data/
│   ├── raw/                   # Raw CSV data
│   ├── processed/             # Parquet outputs
│   └── sample_data/           # Small test datasets
│
├── etl/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── spark_jobs/
│       ├── main.py           # Main ETL orchestrator
│       ├── extract.py        # Data extraction
│       ├── transform.py      # Transformations
│       └── load.py           # Data loading
│
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py              # FastAPI application
│   ├── routers/             # API endpoints
│   └── tests/               # API tests
│
├── dashboard/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py              # Main dashboard
│   └── pages/              # Multi-page app
│
├── database/
│   ├── init.sql            # Database schema
│   └── seed.sql            # Sample data
│
└── scripts/
    └── generate_data.py    # Data generation script
```

## 📖 Usage Guide

### Make Commands

```bash
# View all available commands
make help

# Data generation
make generate-data          # Generate synthetic data

# Docker operations
make build                  # Build all images
make up                     # Start all services
make down                   # Stop all services
make restart                # Restart all services

# ETL pipeline
make run-etl               # Run ETL pipeline

# Logs
make logs                  # View all logs
make logs-api              # API logs only
make logs-dashboard        # Dashboard logs only
make logs-etl              # ETL logs only

# Database
make db-shell              # Access PostgreSQL CLI

# Cleanup
make clean                 # Remove containers and data
```

### Running ETL Pipeline

The ETL pipeline processes raw data and creates analytical tables:

```bash
# Run the pipeline
make run-etl

# The pipeline will:
# 1. Extract data from CSV files
# 2. Clean and validate data
# 3. Perform transformations
# 4. Create aggregated tables
# 5. Save to PostgreSQL and Parquet
```

### Using the Dashboard

1. Navigate to http://localhost:8501
2. Use the sidebar for navigation
3. Apply date filters as needed
4. View multiple analytics pages:
   - Sales Overview
   - Product Performance
   - Customer Insights
   - Data Quality

### Using the API

Access the interactive API documentation at http://localhost:8000/docs

Example API calls:

```bash
# Get sales summary
curl http://localhost:8000/sales/summary

# Get top products
curl http://localhost:8000/products/top?metric=revenue&limit=10

# Get customer segments
curl http://localhost:8000/customers/segments

# Get daily sales with date filter
curl "http://localhost:8000/sales/daily?start_date=2024-01-01&limit=30"
```

## 📚 API Documentation

### Sales Endpoints

- `GET /sales/summary` - Overall sales metrics
- `GET /sales/daily` - Daily sales data with date filtering
- `GET /sales/monthly` - Monthly trends

### Product Endpoints

- `GET /products/top` - Top products by revenue/units/rating
- `GET /products/{product_id}` - Product details
- `GET /products/categories` - Category performance

### Customer Endpoints

- `GET /customers/segments` - Customer segmentation
- `GET /customers/geographic` - Geographic performance

### System Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /data-quality/metrics` - Data quality metrics
- `GET /etl/history` - ETL run history

## 🔧 Development

### Local Development Setup

```bash
# Start only the database
docker-compose up -d postgres

# Run API locally (for development)
cd api
pip install -r requirements.txt
python main.py

# Run Streamlit locally
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

### Running Tests

```bash
# Run API tests
docker-compose exec api pytest tests/ -v

# Run with coverage
docker-compose exec api pytest tests/ --cov=. --cov-report=html
```

### Adding New Features

1. **New API Endpoint**:
   - Add route in `api/routers/`
   - Update schemas in `api/models/schemas.py`
   - Add tests in `api/tests/`

2. **New Dashboard Page**:
   - Create file in `dashboard/pages/`
   - Add navigation in sidebar

3. **New ETL Transformation**:
   - Add function in `etl/spark_jobs/transform.py`
   - Update main orchestrator
   - Create new analytical table in database

## 🚀 Deployment Considerations

### Serverless vs. Serverfull

#### Serverless Deployment
**Pros:**
- Auto-scaling
- Pay per execution
- No server management

**Cons:**
- Cold start latency
- Execution time limits
- More complex architecture

**Example:** AWS Lambda + API Gateway + RDS

#### Serverfull Deployment
**Pros:**
- Consistent performance
- Simpler architecture
- More control

**Cons:**
- Fixed costs
- Manual scaling
- Server maintenance

**Example:** EC2 + ECS + RDS

### Cloud Deployment Options

#### AWS
- **ETL**: EMR or Glue
- **Database**: RDS (PostgreSQL)
- **API**: ECS or Lambda
- **Dashboard**: ECS or Fargate

#### GCP
- **ETL**: Dataproc
- **Database**: Cloud SQL
- **API**: Cloud Run
- **Dashboard**: Cloud Run

#### Azure
- **ETL**: Azure Databricks
- **Database**: Azure Database for PostgreSQL
- **API**: Container Instances
- **Dashboard**: Container Instances

## 🐛 Troubleshooting

### Common Issues

#### Docker Container Fails to Start

```bash
# Check container logs
docker-compose logs <service-name>

# Rebuild containers
make down
make build
make up
```

#### PostgreSQL Connection Error

```bash
# Ensure PostgreSQL is healthy
docker-compose ps

# Check logs
make logs-db

# Restart database
docker-compose restart postgres
```

#### ETL Pipeline Fails

```bash
# Check ETL logs
make logs-etl

# Verify data files exist
ls -la data/raw/

# Verify database connection
make db-shell
```

#### Dashboard Shows No Data

```bash
# Verify API is running
curl http://localhost:8000/health

# Check if ETL has run successfully
make logs-etl

# Verify data in database
make db-shell
\dt analytics.*
SELECT COUNT(*) FROM analytics.sales_summary;
```

#### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

## 📈 Learning Outcomes

By completing this project, you will have practical experience with:

### PySpark & ETL
- Reading data from multiple sources
- Data cleaning and validation
- Complex transformations and aggregations
- Writing to multiple targets (PostgreSQL, Parquet)
- ETL orchestration and error handling

### Containerization
- Writing Dockerfiles
- Multi-container orchestration with Docker Compose
- Container networking
- Volume management
- Environment configuration

### API Development
- RESTful API design
- Request validation with Pydantic
- Database integration with SQLAlchemy
- API documentation with FastAPI
- Error handling and logging

### Dashboard Development
- Interactive visualizations with Plotly
- Multi-page applications with Streamlit
- API integration
- State management
- User experience design

### Database Design
- Schema design for analytics
- Indexing strategies
- Query optimization
- Data warehouse concepts

### DevOps Practices
- Automation with Makefiles
- Environment management
- Logging and monitoring
- Testing strategies

## 🎓 Next Steps

1. **Add More Features**:
   - Real-time data ingestion
   - Email alerts for anomalies
   - Advanced analytics (forecasting, clustering)
   - User authentication

2. **Improve Performance**:
   - Optimize SQL queries
   - Add caching layer (Redis)
   - Implement data partitioning
   - Add query result caching

3. **Deploy to Cloud**:
   - Set up CI/CD pipeline
   - Deploy to AWS/GCP/Azure
   - Implement monitoring (Prometheus, Grafana)
   - Set up automated backups

4. **Add Testing**:
   - Unit tests for all components
   - Integration tests
   - Load testing
   - Data quality tests

## 📄 License

This project is created for educational purposes.

## 🤝 Contributing

Feel free to fork, improve, and submit pull requests!

## 📧 Contact

Questions? Open an issue or reach out!

---

**Happy Learning! 🚀**
