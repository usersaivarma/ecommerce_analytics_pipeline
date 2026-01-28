.PHONY: help setup build up down logs clean test run-etl generate-data

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup         - Initial project setup"
	@echo "  make generate-data - Generate synthetic e-commerce data"
	@echo "  make build         - Build all Docker images"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make run-etl       - Run ETL pipeline"
	@echo "  make logs          - View logs from all services"
	@echo "  make logs-api      - View API logs"
	@echo "  make logs-dashboard- View dashboard logs"
	@echo "  make logs-etl      - View ETL logs"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Remove containers, volumes, and generated data"
	@echo "  make restart       - Restart all services"

# Initial setup
setup:
	@echo "Setting up project..."
	mkdir -p data/raw data/processed data/sample_data
	cp .env.example .env
	@echo "Setup complete! Edit .env file with your configuration."

# Generate synthetic data
generate-data:
	@echo "Generating synthetic e-commerce data..."
	python scripts/generate_data.py
	@echo "Data generation complete!"

# Build all Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	sleep 10
	docker-compose up -d api dashboard
	@echo "Services started!"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Dashboard: http://localhost:8501"

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Run ETL pipeline
run-etl:
	@echo "Running ETL pipeline..."
	docker-compose up etl
	@echo "ETL pipeline completed!"

# View logs
logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-dashboard:
	docker-compose logs -f dashboard

logs-etl:
	docker-compose logs etl

logs-db:
	docker-compose logs -f postgres

# Run tests
test:
	@echo "Running tests..."
	docker-compose exec api pytest tests/
	@echo "Tests complete!"

# Clean up
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf data/processed/*
	@echo "Cleanup complete!"

# Restart services
restart: down up

# Full pipeline: build, generate data, run ETL, start services
full-setup: setup generate-data build run-etl up
	@echo "Full setup complete!"
	@echo "Access the dashboard at http://localhost:8501"

# Check service status
status:
	@echo "Service status:"
	docker-compose ps

# Access database CLI
db-shell:
	docker-compose exec postgres psql -U ecommerce_user -d ecommerce_analytics

# Access API container shell
api-shell:
	docker-compose exec api /bin/bash

# View API documentation
api-docs:
	@echo "Opening API documentation..."
	@echo "Visit: http://localhost:8000/docs"
