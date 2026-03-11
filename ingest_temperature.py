import requests
import csv
from datetime import datetime, timedelta
import time

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

def save_to_csv(filename, temperatures, timestamps):
    """Save temperature data to CSV file"""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "Temperature (°C)"])
        
        for timestamp, temp in zip(timestamps, temperatures):
            writer.writerow([timestamp, temp])

def main():
    # Sao Paulo coordinates
    latitude = -23.5505
    longitude = -46.6333
    
    # Get current time and calculate 24 hours ago
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    print("Fetching hourly temperature data for Sao Paulo...")
    
    try:
        temperatures, timestamps = get_hourly_temperature(latitude, longitude, start_time, end_time)
        
        # Convert timestamps to readable format
        formatted_timestamps = [datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S") for ts in timestamps]
        
        # Save to CSV
        csv_filename = "sao_paulo_temperature_log.csv"
        save_to_csv(csv_filename, temperatures, formatted_timestamps)
        
        print(f"Data successfully saved to {csv_filename}")
        print(f"Fetched {len(temperatures)} hourly data points")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()