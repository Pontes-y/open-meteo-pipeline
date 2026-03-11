# open-meteo-pipeline
Data pipeline to ingest, transform and test temperature data.

## Local Development

### Basic Usage

1. Install required dependencies:
   ```bash
   pip install requests
   ```

2. Run the script:
   ```bash
   python ingest_temperature.py
   ```

3. The script will:
   - Fetch hourly temperature data for Sao Paulo from the Open-Meteo API
   - Save the data to `sao_paulo_temperature_log.csv`
   - Display the number of data points fetched

### AWS Deployment

This project includes AWS Lambda functions and Step Functions for production deployment.

#### Prerequisites
- AWS account with appropriate permissions
- S3 buckets:
  - Development: `arn:aws:s3:::open-meteo-pipeline-dev`
  - Production: `arn:aws:s3:::open-meteo-pipeline-prod`
- RDS PostgreSQL databases:
  - Development: `open-meteo-pipeline-dev`
  - Production: `open-meteo-pipeline-prod`
- IAM roles for Lambda and Step Functions

#### Deployment Package
1. Build the deployment package:
   ```bash
   cd lambda_package
   ./package.sh
   ```

2. The package includes:
   - `lambda_handler.py` - Main Lambda function for data ingestion
   - `transform_handler.py` - Lambda function for data transformation
   - All dependencies in `requirements.txt`

#### AWS Resources
- **Lambda Functions:**
  - `ingest-temperature` - Fetches data and saves to S3
  - `transform-temperature` - Transforms CSV and uploads to RDS

- **Step Functions:**
  - State machine: `open-meteo-pipeline`
  - Triggers both Lambda functions in sequence

- **S3:**
  - Development: `arn:aws:s3:::open-meteo-pipeline-dev`
  - Production: `arn:aws:s3:::open-meteo-pipeline`
  - Folder structure: `sao_paulo/YYYY_MM_DD_HHMMSS.csv`

- **RDS:**
  - Development: `temperature_data_dev` table in `open-meteo-pipeline-dev` database
  - Production: `temperature_data` table in `open-meteo-pipeline` database

## GitHub Actions CI/CD

The project includes automated CI/CD pipeline:

### Workflow
- **Test**: Runs on every push/pull request
- **Build**: Creates deployment package
- **Deploy**: Deploys to AWS on main branch pushes

### Required Secrets
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `STEP_FUNCTIONS_ROLE_ARN` - IAM role for Step Functions
- `S3_BUCKET` - S3 bucket ARN (defaults to dev/production based on environment)
- `RDS_HOST` - RDS host address
- `RDS_DB` - RDS database name
- `RDS_USER` - RDS username
- `RDS_PASSWORD` - RDS password

## Output

The pipeline generates:
- CSV files in S3 with organized folder structure
- Temperature data stored in RDS database
- Structured data with city, timestamp, and temperature

## Environment Configuration

### Local Development
- Uses development environment by default
- S3 bucket: `arn:aws:s3:::open-meteo-pipeline-dev`
- RDS table: `temperature_data_dev`

### Production
- Set `ENVIRONMENT=prod` to use production resources
- S3 bucket: `arn:aws:s3:::open-meteo-pipeline`
- RDS table: `temperature_data`

## Requirements

- Python 3.6+
- requests library
- boto3 library
- psycopg2-binary library
