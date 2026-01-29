FROM apache/spark-py:v3.4.0

USER root

# Install required packages
RUN apt-get update && \
    apt-get install -y wget && \
    rm -rf /var/lib/apt/lists/*

# Download PostgreSQL JDBC driver
RUN wget -P /opt/spark/jars/ https://jdbc.postgresql.org/download/postgresql-42.5.0.jar

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY spark_jobs/ ./spark_jobs/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the ETL job
CMD ["python", "spark_jobs/main.py"]
