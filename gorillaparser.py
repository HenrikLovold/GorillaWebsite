import os
import time
import regex as re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SERVICE_ACCOUNT_FILE = "" # Set by gorilla_analyze.py
SPREADSHEET_ID = '1Q2ESxU3V-53BPc90RD4r-4j_0MP2vRCv7Q_h-8mAb98'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


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


def read_sheet_data(spreadsheet_id, ranges, credentials):
    try:
        service = build('sheets', 'v4', credentials=credentials)
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=ranges
        ).execute()
        value_ranges = result.get('valueRanges', [])
        if not value_ranges:
            print(f'No data found in the specified ranges: {ranges}')
            return []
        else:
            print(f'Successfully retrieved data from ranges: {ranges}')
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
    try:
        service = build('sheets', 'v4', credentials=credentials)
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
    
def calc_avg(item_values, item):
    n = 0
    s = 0
    for k, v in item_values[item].items():
        if k == "avg":
            continue
        s += v
        n += 1
    return round(s/n, 2)
    
def get_prices(testing=False, n_test=0):
    credentials = authenticate_service_account()

    if credentials:
        item_values = {}
        sheet_names = get_sheet_names(SPREADSHEET_ID, credentials)

        test_i = 0
        for sheet in sheet_names:
            time.sleep(0.5)
            if not sheet.startswith("["):
                continue
            datematch_regex = r"\[(.*?)\]"
            date = re.match(datematch_regex, sheet).group()[1:-1] + "." + sheet[-1]
            KEY_RANGE = f'{sheet}!B8:B'
            VALUE_RANGE = f'{sheet}!D8:D'
            RANGES_TO_READ = [
                KEY_RANGE,
                VALUE_RANGE
            ]
            print(f"\n--- Fetching Data from {sheet} ---")
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
                            item_values[item][date] = price
                            item_values[item]["avg"] = calc_avg(item_values, item)                              
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

if __name__ == '__main__':
    get_prices()