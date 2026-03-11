import json
import boto3
import csv
import psycopg2
from datetime import datetime

def transform_and_upload_to_rds(event, context):
    """Lambda function to transform CSV and upload to RDS"""
    # Get S3 bucket and key from event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']
    
    # Get environment from event or default to dev
    environment = os.environ.get('ENVIRONMENT', 'dev')
    
    # Initialize S3 and RDS clients
    s3_client = boto3.client('s3')
    rds_client = boto3.client('rds')
    
    try:
        # Download CSV from S3
        csv_obj = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        csv_content = csv_obj['Body'].read().decode('utf-8').splitlines()
        
        # Parse CSV
        reader = csv.DictReader(csv_content)
        data = [row for row in reader]
        
        # Connect to RDS
        conn = psycopg2.connect(
            host=os.environ.get('RDS_HOST'),
            database=os.environ.get('RDS_DB'),
            user=os.environ.get('RDS_USER'),
            password=os.environ.get('RDS_PASSWORD')
        )
        
        # Use environment-specific table if needed
        table_name = f"temperature_data_{environment}" if environment != 'prod' else "temperature_data"
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                city VARCHAR(100),
                timestamp TIMESTAMP,
                temperature DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert data
        city = s3_key.split('/')[0]
        for row in data:
            cursor.execute(f"""
                INSERT INTO {table_name} (city, timestamp, temperature)
                VALUES (%s, %s, %s)
            """, (city, row['Timestamp'], float(row['Temperature (°C)'])))
        
        # Commit and close
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully uploaded {len(data)} records to RDS',
                'city': city,
                's3_key': s3_key,
                'environment': environment,
                'table': table_name
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }