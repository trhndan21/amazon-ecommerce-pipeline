# Amazon Product Analytics Pipeline 🛒📊

> **End-to-End Data Engineering Project**: Build a pipeline to process Amazon sales data from raw (Raw CSV) to an analytical Dashboard, using Docker, Airflow, Spark, and Postgres.

## 1. Overview
This project builds an automated Data Pipeline to analyze sales data and customer reviews on Amazon. The system processes raw data (multiple lines, error format), cleans, classifies customer sentiment (Sentiment Analysis), and displays visual reports.

**Objects:**
* Big Data Processing with Spark.
* Orchestration with Airflow.
* Build a standard Data Warehouse (Raw -> Clean -> Serving).

## 2. Architecture

![Architecture Diagram](images/diagram.png)

Data Flow:
1.  **Ingestion:** Upload CSV data to **MinIO** (Data Lake - Raw Layer).
2.  **Processing:** **Apache Spark** reads data, processes price columns (`₹`, `%`), cleans review text and classifies sentiment(Positive/Negative).
3.  **Storage:** Save clean data to MinIO (Parquet) and load to **Postgres** (Data Warehouse).
4.  **Visualization:** **Quarto** queries data from Postgres and creates an HTML Dashboard.

## 3. Tech Stack

* **Containerization:** Docker, Docker Compose.
* **Orchestration:** Apache Airflow (2.9.2).
* **Processing:** Apache Spark (PySpark 3.5).
* **Storage:** MinIO (S3 Compatible), PostgreSQL (Data Warehouse).
* **Visualization:** Quarto, Plotly.
* **Language:** Python, SQL.

## 4. Key Challenges

During the implementation, I solved practical technical problems:

* **Multi-arch Support:** Customizing Dockerfile to make Spark and Java run stably on **Apple Silicon (ARM64)** và Intel (AMD64) chips.
* **Handing Dirty Data:**
    * Handling Multiline CSVs that cause Spark to misread.
    * Cleaning up price columns containing strange characters (Currency symbols) using Regex.
    * Handling inconsistent Schema (Schema Evolution) between data files.
* **Optimization:** Using the **Parquet** format to optimize storage and read/write speed compared to CSV.
