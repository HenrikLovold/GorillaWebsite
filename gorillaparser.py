import os
import time
import regex as re
import statistics as stat
import traceback
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
        if k.startswith("2"):
            s += v
            n += 1
    return round(s/n, 2) if n != 0 else 0

def calc_variance(item_values, item):
    values = [v for k, v in item_values[item].items() if k.startswith("2")]
    if len(values) > 1:
        item_values[item]["var"] = round(stat.variance(values), 2)
    else:
        item_values[item]["var"] = 0
    
def calc_stdev(item_values, item):
    values = [v for k, v in item_values[item].items() if k.startswith("2")]
    if len(values) > 1:
        item_values[item]["stdev"] = round(stat.stdev(values), 2)
    else:
        item_values[item]["stdev"] = 0

def calc_avg_spending(player_spendings, player_cuts):
    for k, v in player_spendings.items():
        if k in player_cuts.keys():
            n_raids = len([x for x in player_cuts[k] if x.startswith("2")])
            sum_spending = sum([float(val) for key, val 
                                in v.items() 
                                if key.startswith("2")])
            v["avg"] = round(sum_spending / n_raids, 2)  if n_raids != 0 else 0

def calc_total_cuts(player_cuts):
    for name, values in player_cuts.items():
        values["total"] = sum([v for k, v in values.items() if k.startswith("2")])

def calc_avg_deduct(player_cuts, player_deducts):
    for name_cut, value_cut in player_cuts.items():
        n_raids = len([v for k, v in value_cut.items() if k.startswith("2")])
        if name_cut in player_deducts.keys():
            player_deducts[name_cut]["avg"] = sum([float(v) for k, v 
                                                   in player_deducts[name_cut].items() 
                                                   if k.startswith("2")]) / n_raids if n_raids != 0 else 0
        else:
            player_deducts[name_cut] = {"avg": 0}


def make_item_values_dict(items, prices, date, item_values):
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
                item_values[item]["stdev"] = 0
                item_values[item]["var"] = 0
                item_values[item][date] = price
        except Exception as e:
            print("Make values dict: Could not parse", items[i][0], prices[i][0], len(prices[i][0]), e)

def make_player_cut_dict(players, cuts, date, player_cuts):
    for i in range(len(players)):
        try:
            player_name = None
            if players[i]:
                player_name = players[i][0]
            if player_name == "" or player_name is None or player_name.isnumeric() or player_name == "Player":
                continue
            player_name.strip()
            price = float(cuts[i][0])
            if players[i] == []:
                break
            if player_name in player_cuts.keys():
                player_cuts[player_name][date] = price
                player_cuts[player_name]["avg"] = calc_avg(player_cuts, player_name)   
                player_cuts[player_name]["total"] += price
            else:
                player_cuts[player_name] = {"avg": price, "total": price}
                player_cuts[player_name][date] = price
        except Exception as e:
            print("Make cut dict: Could not parse i=", i, e)

def make_player_spend_dict(players, prices, date, player_spendings):
    for i in range(len(players)):
        try:
            player_name = players[i][0].strip()
            if player_name == "" or player_name.isnumeric() or player_name == "Player":
                continue
            player_name = player_name.split("-")[0]
            price = float(prices[i][0])
            if players[i] == []:
                break
            if player_name in player_spendings.keys():
                if date in player_spendings[player_name]:
                    player_spendings[player_name][date] += price
                else:
                    player_spendings[player_name][date] = price
                player_spendings[player_name]["avg"] = calc_avg(player_spendings, player_name)     
                player_spendings[player_name]["total"] += price                         
            else:
                player_spendings[player_name] = {"avg": price, "total": price}
                player_spendings[player_name][date] = price
        except Exception as e:
            print("Make spend dict: Could not parse i=", i, players[i][0], prices[i][0], len(prices[i][0]), e)
    
def make_deduct_dict(names, pcts, date, player_deducts):
    for name, pct in zip(names, pcts):
        if not name:
            continue
        name = name[0]
        total_deduct = sum([float(i[:-1]) for i in pct])
        if not name in player_deducts:
            player_deducts[name] = {"avg": 0, date: total_deduct}
        if not date in player_deducts[name]:
            player_deducts[name][date] = total_deduct

def make_misc_player_stats(player_cuts, player_spendings, misc):
    for name in player_cuts:
        cuts = [v for k, v in player_cuts[name].items() if k.startswith("2")]
        misc[name] = {"ratio": 0, "most_spent": 0, "biggest_cut": max(cuts), "avg_deduct": "TBA"}
    for cut_name, cut_val in player_cuts.items():
        if cut_name in player_spendings.keys():
            spendings = [v for k, v in player_spendings[cut_name].items() if k.startswith("2")]
            misc[cut_name]["ratio"] =  round(player_spendings[cut_name]["avg"] / cut_val["avg"], 2) \
                                       if cut_val["avg"] != 0 else 0
            misc[cut_name]["most_spent"] = max(spendings)

def get_prices_and_players(testing=False, n_test=0):
    credentials = authenticate_service_account()

    if credentials:
        item_values = {}
        player_cuts = {}
        player_spendings = {}
        player_deducts = {}
        player_misc = {}
        sheet_names = get_sheet_names(SPREADSHEET_ID, credentials)

        test_i = 0
        for sheet in sheet_names:
            time.sleep(0.5) # To avoid throttling from Google
            if not sheet.startswith("["):
                continue
            datematch_regex = r"\[(.*?)\]"
            date = re.match(datematch_regex, sheet).group()[1:-1] + "." + sheet[-1] # pyright: ignore[reportOptionalMemberAccess]
            KEY_RANGE_ITEMS = f'{sheet}!B8:B63'
            VALUE_RANGE_ITEMS = f'{sheet}!D8:D63'
            KEY_RANGE_PLAYERS = f'{sheet}!E8:E63'
            VALUE_RANGE_PLAYERS = f'{sheet}!H8:H63'
            VALUE_RANGE_BUYERS = f'{sheet}!C8:C63'
            VALUE_RANGE_DEDUCT_NAMES = f'{sheet}!I8:I63'
            VALUE_RANGE_DEDUCT_PCTS = f'{sheet}!L8:L63'
            RANGES_TO_READ = [
                KEY_RANGE_ITEMS,
                VALUE_RANGE_ITEMS,
                KEY_RANGE_PLAYERS,
                VALUE_RANGE_PLAYERS,
                VALUE_RANGE_BUYERS,
                VALUE_RANGE_DEDUCT_NAMES,
                VALUE_RANGE_DEDUCT_PCTS
            ]
            print(f"\n--- Fetching Data from {sheet} ---")
            value_ranges = read_sheet_data(SPREADSHEET_ID, RANGES_TO_READ, credentials)
            if not value_ranges:
                raise RuntimeError("Value ranges invalid")
            items = value_ranges[0]["values"] # pyright: ignore[reportOptionalSubscript]
            prices = value_ranges[1]["values"] # type: ignore
            players = value_ranges[2]["values"]
            cuts = value_ranges[3]["values"]
            buyers = value_ranges[4]["values"]
            if "values" in value_ranges[5].keys() and "values" in value_ranges[6].keys():
                deduct_names = value_ranges[5]["values"]
                deduct_pcts = value_ranges[6]["values"]
            else:
                deduct_names = [[]]
                deduct_pcts = [[]]
            try:
                for i in range(len(items)):
                    make_item_values_dict(items, prices, date, item_values)
                for i in range(len(players)):
                    make_player_cut_dict(players, cuts, date, player_cuts)
                make_player_spend_dict(buyers, prices, date, player_spendings)
                make_deduct_dict(deduct_names, deduct_pcts, date, player_deducts)
            except Exception as e: # You should never do this in code, but it works... crap
                print(e)
                traceback.print_exc()

            test_i += 1
            if testing and test_i > n_test:
                break
        for item in item_values:
            calc_variance(item_values, item)
            calc_stdev(item_values, item)
        calc_avg_spending(player_spendings, player_cuts)
        calc_total_cuts(player_cuts)
        calc_avg_deduct(player_cuts, player_deducts)
        make_misc_player_stats(player_cuts, player_spendings, player_misc)
        return (item_values, player_cuts, player_spendings, player_deducts, player_misc)

if __name__ == '__main__':
    get_prices_and_players()