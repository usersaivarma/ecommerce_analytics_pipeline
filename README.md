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

This project is created for educational purposes.

## 🤝 Contributing

Feel free to fork, improve, and submit pull requests!

## 📧 Contact

Questions? Open an issue or reach out!

---

**Happy Learning! 🚀**
