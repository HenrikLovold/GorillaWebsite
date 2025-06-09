import os
import time
import regex as re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# Removed pandas import

# --- Configuration ---
# Replace with the path to your downloaded Service Account JSON key file
SERVICE_ACCOUNT_FILE = ""

# Replace with the ID of your Google Sheet
# The ID is the long string of characters in the sheet's URL between /d/ and /edit
# Example: https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
SPREADSHEET_ID = '1Q2ESxU3V-53BPc90RD4r-4j_0MP2vRCv7Q_h-8mAb98'

# Define the ranges you want to read as a list of strings.
# Use A1 notation. 'SheetName!ColumnStartRow:ColumnEndRow'
# To read from a row down to the end of the column, omit the EndRow (e.g., 'Sheet1!B8:B')
# Using the sheet name provided by the user.


# The scope defines the permissions your script will have.
# 'https://www.googleapis.com/auth/spreadsheets.readonly' allows reading only.
# Use 'https://www.googleapis.com/auth/spreadsheets' for read and write access.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# --- Authentication ---
def authenticate_service_account():
    """Authenticates using a Service Account and returns credentials."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Error: Service account file not found at {SERVICE_ACCOUNT_FILE}")
        print("Please ensure the file path is correct and the file exists.")
        return None

    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        print("Authentication successful.")
        return creds
    except Exception as e:
        print(f"Error during service account authentication: {e}")
        return None

# --- Read Data from Sheet (Supports multiple ranges) ---
def read_sheet_data(spreadsheet_id, ranges, credentials):
    """Reads data from specified ranges in a Google Sheet."""
    try:
        service = build('sheets', 'v4', credentials=credentials)

        # Call the Sheets API to get values from multiple ranges
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=ranges # Pass the list of ranges here
        ).execute()

        # The response contains a list of ValueRange objects, one for each requested range
        value_ranges = result.get('valueRanges', [])

        if not value_ranges:
            print(f'No data found in the specified ranges: {ranges}')
            # Return an empty list if no value ranges are found
            return []
        else:
            print(f'Successfully retrieved data from ranges: {ranges}')
            # Return the raw list of ValueRange objects
            return value_ranges

    except HttpError as error:
        print(f'An API error occurred while reading data: {error}')
        print(f'Check if the spreadsheet ID ({spreadsheet_id}) and ranges ({ranges}) are correct.')
        print(f'Also ensure the service account has permission to access the sheet.')
        return None
    except Exception as e:
        print(f'An unexpected error occurred while reading data: {e}')
        return None

# --- Get Sheet Names (Remains the same) ---
def get_sheet_names(spreadsheet_id, credentials):
    """Retrieves the names of all sheets (tabs) in a Google Sheet."""
    try:
        service = build('sheets', 'v4', credentials=credentials)

        # Call the Sheets API to get spreadsheet metadata
        # We use the 'fields' parameter to request only the sheet titles for efficiency
        spreadsheet_metadata = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields='sheets.properties.title'
        ).execute()

        sheet_titles = []
        if 'sheets' in spreadsheet_metadata:
            for sheet in spreadsheet_metadata['sheets']:
                if 'properties' in sheet and 'title' in sheet['properties']:
                    sheet_titles.append(sheet['properties']['title'])

        if not sheet_titles:
            print('No sheets found in the spreadsheet.')
            return []
        else:
            print(f'Successfully retrieved sheet names for spreadsheet ID: {spreadsheet_id}')
            return sheet_titles

    except HttpError as error:
        print(f'An API error occurred while getting sheet names: {error}')
        print(f'Check if the spreadsheet ID ({spreadsheet_id}) is correct.')
        print(f'Also ensure the service account has permission to access the spreadsheet.')
        return None
    except Exception as e:
        print(f'An unexpected error occurred while getting sheet names: {e}')
        return None
    
def get_prices(testing=False, n_test=0):
    credentials = authenticate_service_account()

    if credentials:
        item_values = {}

# Define the specific ranges for keys and values
        # Get and print sheet names (optional, but useful)
        sheet_names = get_sheet_names(SPREADSHEET_ID, credentials)

        test_i = 0
        for sheet in sheet_names:
            time.sleep(0.5)
            if not sheet.startswith("["):
                continue
            datematch_regex = r"\[(.*?)\]"
            date = re.match(datematch_regex, sheet).group()[1:-1] + "." + sheet[-1]
            KEY_RANGE = f'{sheet}!B8:B' # Data for dictionary keys (will be in keys_data list)
            VALUE_RANGE = f'{sheet}!D8:D' # Data for dictionary values (will be in values_data list)

            RANGES_TO_READ = [
                KEY_RANGE,
                VALUE_RANGE
            ]
            # Read data from the specified ranges (keys and values)
            print(f"\n--- Fetching Data from {sheet} ---")
            # read_sheet_data now returns the raw value_ranges list
            value_ranges = read_sheet_data(SPREADSHEET_ID, RANGES_TO_READ, credentials)
            items = value_ranges[0]["values"]
            prices = value_ranges[-1]["values"]
            try:
                raid_num = 0
                for i in range(len(items)):
                    try:
                        item = items[i][0].strip()
                        item = item.replace(",", "")
                        price = float(prices[i][0])
                        if items[i] == []:
                            break
                        if item in item_values.keys():
                            #item_values[item]["avg"] = round(float((item_values[item]["avg"] + price) / 2), 2)
                            item_values[item][date] = price
                            curr_avg = 0
                            n = 0
                            for key, val in item_values.items():
                                if key != "avg":
                                    n += 1
                                    curr_avg += float(val)
                            item_values[item]["avg"] = round(float(curr_avg / n), 2)
                        else:
                            item_values[item] = {"avg": price}
                            item_values[item][date] = price
                    except Exception as e:
                        print("Could not parse", items[i][0], prices[i][0], len(prices[i][0]), e)
                    raid_num += 1
            except: # You should never do this in code, but it works... crap
                if testing:
                    test_i += 1
                    if test_i > n_test:
                        break
                continue
            i += 1
        return item_values



# --- Main Execution ---
if __name__ == '__main__':
    get_prices()