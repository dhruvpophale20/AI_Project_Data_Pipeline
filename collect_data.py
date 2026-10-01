import os
import json
import requests
import gspread

from datetime import datetime
from google.oauth2.service_account import Credentials


# ============================================================
# CONFIGURATION
# ============================================================

# Rajkot coordinates
LATITUDE = 22.3039
LONGITUDE = 70.8022

# Google Sheet ID
SPREADSHEET_ID = "1Y27myXpvTLqFWdSUvvTnSi5cowVLV0qiHbJ-PL77HHE"

# Google Sheet worksheet/tab name
WORKSHEET_NAME = "AirQualityData"


# ============================================================
# GOOGLE SHEETS COLUMNS
# ============================================================

HEADERS = [
    "timestamp",
    "pm2_5",
    "pm10",
    "co",
    "no2",
    "so2",
    "o3",
    "temperature",
    "relative_humidity",
    "wind_speed",
    "wind_direction",
    "precipitation"
]


# ============================================================
# CONNECT TO GOOGLE SHEETS
# ============================================================

def connect_google_sheet():

    # Read Google service-account credentials
    # from environment variable
    credentials_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]

    credentials_info = json.loads(credentials_json)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    # Open spreadsheet using Sheet ID
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # Open worksheet/tab
    worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

    return worksheet


# ============================================================
# GET AIR QUALITY DATA
# ============================================================

def get_air_quality():

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,

        "current": (
            "pm2_5,"
            "pm10,"
            "carbon_monoxide,"
            "nitrogen_dioxide,"
            "sulphur_dioxide,"
            "ozone"
        ),

        "timezone": "Asia/Kolkata"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()["current"]


# ============================================================
# GET WEATHER DATA
# ============================================================

def get_weather():

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "precipitation"
        ),

        "timezone": "Asia/Kolkata"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()["current"]


# ============================================================
# CREATE DATA ROW
# ============================================================

def create_row():

    air = get_air_quality()
    weather = get_weather()

    # Current timestamp in local timezone
    timestamp = datetime.now().astimezone().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    row = [
        timestamp,

        # Air quality
        air.get("pm2_5"),
        air.get("pm10"),
        air.get("carbon_monoxide"),
        air.get("nitrogen_dioxide"),
        air.get("sulphur_dioxide"),
        air.get("ozone"),

        # Weather
        weather.get("temperature_2m"),
        weather.get("relative_humidity_2m"),
        weather.get("wind_speed_10m"),
        weather.get("wind_direction_10m"),
        weather.get("precipitation")
    ]

    return row


# ============================================================
# SAVE DATA TO GOOGLE SHEETS
# ============================================================

def save_to_google_sheet(row):

    worksheet = connect_google_sheet()

    # Create headers if the worksheet is empty
    if not worksheet.get_all_values():

        worksheet.append_row(
            HEADERS,
            value_input_option="USER_ENTERED"
        )

    # Add the new data row
    worksheet.append_row(
        row,
        value_input_option="USER_ENTERED"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("==========================================")
    print("   Rajkot Air Quality Data Collector")
    print("==========================================")

    try:

        print("Collecting air-quality data...")
        row = create_row()

        print("Data collected:")
        print(row)

        print("Saving data to Google Sheets...")
        save_to_google_sheet(row)

        print("Data successfully saved.")

    except Exception as error:

        print("ERROR:")
        print(error)

        raise


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
