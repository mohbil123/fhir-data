# FHIR Data Processing Pipeline

This project implements a scalable pipeline to process FHIR (Fast Healthcare Interoperability Resources) patient and encounter data. The data is extracted from a JSON file following the FHIR format, transformed, and then stored into a relational database (MySQL). The goal is to make this data easily queryable for further analysis, reporting, and visualisation.

## Features

- **FHIR Data Parsing**: Processes `Patient` and `Encounter` resources from FHIR JSON files.
- **MySQL Storage**: Inserts parsed data into MySQL tables (`patients` and `encounters`).
- **Batch Processing**: Optimises the insertion of multiple records at once for efficient data handling.
- **Logging and Error Handling**: Provides logs for actions and handles errors gracefully.

## Project Structure
```
├── src                    
│   ├── db_config.py           # Database configuration and session handling
│   └──  fhir_processor.py      # Logic to process FHIR data and insert it into MySQL
├── data                       # Directory to hold FHIR JSON files
│   └── fhir_sample.json       # Example FHIR data files
├── tests                      # Directory for test cases
|   ├── test_db_config.py      # DB config test cases
│   └── test_fhir_processor.py # Pytest test cases
├── Dockerfile                 # Docker setup file for containerising the app
├── docker-compose.yml         # Docker Compose configuration for running MySQL and the app
├── requirements.txt           # Python dependencies
├── main.py                    # Entry point to run the application
└── README.md                  # This file

```

## Setup Guide

### 1. Prerequisites

Make sure you have the following installed:

- **Python 3.12+**
- **Docker and Docker Compose**
- **MySQL (optional)**: If you don't want to use Docker for MySQL, you can install MySQL locally.

### 2. Clone the Repository

```bash
git clone https://github.com/mohbil123/fhir-data.git
```
### 3. Create a Virtual Environment and Install Dependencies

It is recommended to use a Python virtual environment to manage dependencies. Run the following commands:

```
python -m venv .venv
source .venv/bin/activate  # On Windows use `.\.venv\Scripts\activate`
pip install -r requirements.txt
```

### 4. Database Configuration

The project uses a MySQL database. You can either run MySQL locally or via Docker. By default, the database connection URL is defined in src/db_config.py:

`DATABASE_URL = "mysql+pymysql://fhiruser:fhirpassword@db:3306/fhir_data"
`

### 5. Running the Application with Docker Compose

To simplify setup, this project includes a docker-compose.yml file that spins up both MySQL and the Python app using Docker. You can start everything with a single command:

`docker-compose up --build`

This command will:

Start a MySQL container with the default credentials.

Run the Python application, which will create the necessary tables in MySQL and process the FHIR data.

### 6. Running the Application Manually

If you prefer not to use Docker, ensure that MySQL is running, and then run the application manually:

1. Make sure MySQL is running and accessible.
1. Run the Python application:

- `python src/main.py`

This will:

- Create the necessary tables (patients, encounters) in MySQL if they don’t already exist.
- Load and process the FHIR data from the JSON file.
- Insert the data into the MySQL tables.

### 7. Testing

Unit tests for the project are written using pytest. To run the tests, ensure pytest is installed, then run:

`pytest tests/`

### 8. Database Tables

The application creates two main tables in the MySQL database:

- patients: Stores basic patient information such as name, gender, birthdate, and address.
- encounters: Stores details of medical encounters including patient reference, status, encounter type, and period.

