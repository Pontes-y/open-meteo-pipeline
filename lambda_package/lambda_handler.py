import json
import os
import requests
import boto3
from datetime import datetime, timedelta
import csv
import io

# Open-Meteo API endpoint for hourly temperature data
API_URL = "https://archive-api.open-meteo.com/v1/archive"

def get_hourly_temperature(latitude, longitude, start_time, end_time):
    """Fetch hourly temperature data from Open-Meteo API"""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_time.strftime("%Y-%m-%d"),
        "end_date": end_time.strftime("%Y-%m-%d"),
        "hourly": "temperature_2m",
        "timezone": "America/Sao_Paulo"
    }
    
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    
    data = response.json()
    return data["hourly"]["temperature_2m"], data["hourly"]["time"]

def save_to_csv(temperatures, timestamps):
    """Save temperature data to CSV file in memory"""
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Timestamp", "Temperature (°C)"])
    
    for timestamp, temp in zip(timestamps, temperatures):
        writer.writerow([timestamp, temp])
    
    return csv_buffer.getvalue()

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    # Sao Paulo coordinates
    latitude = -23.5505
    longitude = -46.6333
    
    # S3 configuration
    environment = os.environ.get('ENVIRONMENT', 'dev')
    s3_bucket = os.environ.get('S3_BUCKET', f'arn:aws:s3:::open-meteo-pipeline{"-prod" if environment == "prod" else ""}')
    city = 'sao_paulo'
    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    s3_key = f"{city}/{timestamp}.csv"
    
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # Get current time and calculate 24 hours ago
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    try:
        temperatures, timestamps = get_hourly_temperature(latitude, longitude, start_time, end_time)
        
        # Convert timestamps to readable format
        formatted_timestamps = [datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S") for ts in timestamps]
        
        # Save to CSV in memory
        csv_content = save_to_csv(temperatures, formatted_timestamps)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=csv_content,
            ContentType='text/csv'
        )
        
        # Get S3 URL
        s3_url = f"https://{s3_bucket}.s3.amazonaws.com/{s3_key}"
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Data successfully saved to S3 bucket {s3_bucket}',
                'data_points': len(temperatures),
                's3_url': s3_url
            })
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error fetching data: {str(e)}'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'An error occurred: {str(e)}'})
        }