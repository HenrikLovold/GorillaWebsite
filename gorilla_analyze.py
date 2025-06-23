import gorillaparser as gp
import time_plotter as tpl
import regex as re
import ast
import logger
import datetime
import time
from sys import argv

LOGGER = logger.Logger()

class GorillaAnalyzer:

    def __init__(self, from_server=True, inp_file="", testing=False, n_test=0):
        self.testing = testing
        self.n_test = n_test
        self.prices: dict = {}
        self.players: dict = {}
        self.buyers: dict = {}
        self.deducts: dict = {}
        self.misc: dict = {}
        if from_server:
            self._fetch_data_from_server()
        else:
            self._read_from_file(inp_file)
        self.n_raids = self._number_of_raids()

    def _fetch_data_from_server(self) -> dict:
        data = gp.get_prices_and_players(self.testing, self.n_test)
        self.prices = data[0]
        self.players = data[1]
        self.buyers = data[2]
        self.deducts = data[3]
        self.misc = data[4]

    def _read_from_file(self, filename):
        name_find_regex = r"^([^{]*)"
        with open(filename, "r") as f:
            for line in f:
                item_name = re.match(name_find_regex, line).group()
                item_name = item_name.strip()
                start_idx = line.index("{")
                dict_str = line[start_idx:].strip()
                dict_parsed = ast.literal_eval(dict_str)
                self.prices[item_name] = dict_parsed

    def _number_of_raids(self) -> int:
        raids = []
        for drop in self.prices.values():
            for date in drop.values():
                if date == "avg":
                    continue
                if date not in raids:
                    raids.append(date)
        return len(raids)
    
    def get_avg_item_value(self, item_name) -> float:
        if item_name in self.prices.keys():
            return self.prices[item_name]["avg"]
        return -1

    def get_drop_dates_for_item(self, item) -> None:
        if not item in self.prices:
            print("Unknown item, or item has never dropped.")
            return
        item_keys = list(self.prices[item].keys())
        item_keys.remove("avg")
        for date in item_keys:
            print(date)

    def get_item_price_at_date(self, item, day, month, year) -> float:
        if len(year) == 2:
            year = "20" + year
        if len(month) == 1:
            month = "0" + month
        if len(day) == 1:
            day = "0" + day
        datestr = f"{year}-{month}-{day}"
        if item in self.prices and datestr in self.prices[item]:
            return self.prices[item][datestr]
        print(item, "not found at date", datestr)
        return -1
    
    def get_item_names(self):
        return list(self.prices.keys())
    
    def get_item_drops(self, item_name):
        if item_name in self.prices.keys():
            return self.prices[item_name]
        raise ValueError("Searched for an item not found in the list...")
    
    def plot_item_value(self, item):
        if item in self.prices:
            tpl.plot_item_prices(item, self.prices[item], tofile=False)
        else:
            print("Item not found, cannot plot values")

    def plot_item_value_to_file(self, item):
        success = True
        if item in self.prices:
            tpl.plot_item_prices(item, self.prices[item], tofile=True)
        else:
            success = False
            print("Item not found, could not plot to file")
        LOGGER.log_entry("Wrote all items to plot: " + str(success))

    def get_item_list(self) -> list:
        items = []
        for item in self.prices.keys():
            items.append(item)
        return items
    
    def get_item_droprate(self, item) -> float:
        ndrops = 0
        if item in self.prices.keys():
            ndrops = len(self.prices[item]) - 1
        return round(ndrops / self.n_raids * 100) 
        
    def dump_to_file(self, filename_prices, filename_players, filename_buyers, filename_deducts, filename_misc) -> None:
        with open(filename_prices, "w") as f:
            for key, value in self.prices.items():
                f.write(str(key) + " " + str(value) + "\n")
        LOGGER.log_entry("Dumped item values to file " + str(filename_prices))
        with open(filename_players, "w") as f:
            for key, value in self.players.items():
                f.write(str(key) + " " + str(value) + "\n")
        LOGGER.log_entry("Dumped player data to file " + str(filename_players))
        with open(filename_buyers, "w") as f:
            for key, value in self.buyers.items():
                f.write(str(key) + " " + str(value) + "\n")
        LOGGER.log_entry("Dumped buyer data to file " + str(filename_buyers))
        with open(filename_deducts, "w") as f:
            for key, value in self.deducts.items():
                f.write(str(key) + " " + str(value) + "\n")
        LOGGER.log_entry("Dumped deduct data to file " + str(filename_deducts))
        with open(filename_misc, "w") as f:
            try:
                for key, value in self.misc.items():
                    f.write(str(key) + " " + str(value) + "\n")
            except:
                LOGGER.log_entry("Error logging misc items")
        LOGGER.log_entry("Dumped misc data to file " + str(filename_misc))

    def daily_update(self):
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        target_time_today_utc = now_utc.replace(hour=4, minute=0, second=0, microsecond=0)
        if now_utc >= target_time_today_utc:
            target_time_utc = target_time_today_utc + datetime.timedelta(days=1)
        else:
            target_time_utc = target_time_today_utc
        time_to_sleep = (target_time_utc - now_utc).total_seconds()
        print(f"Current UTC: {now_utc}")
        print(f"Next run scheduled for UTC: {target_time_utc}")
        print(f"Sleeping for {time_to_sleep:.2f} seconds...")
        time.sleep(time_to_sleep)
        LOGGER.log_entry("Daily update from server")
        self.prices = self._fetch_data_from_server()
        self.dump_to_file("out_list.csv", "player_list.csv", "buyer_list.csv", "deduct_list.csv", "misc_list.csv")
        time.sleep(1)

def main(reload_server=False, reload_file=False):
    if reload_server:
        LOGGER.log_entry("Reloading from server")
        g = GorillaAnalyzer(from_server=True, inp_file="out_list.csv", testing=False, n_test=49)
        for i, k in enumerate(g.prices.keys()):
            g.plot_item_value_to_file(k)
        g.dump_to_file("out_list.csv", "player_list.csv", "buyer_list.csv", "deduct_list.csv", "misc_list.csv")
    if reload_file:
        LOGGER.log_entry("Reloading from file")
        g = GorillaAnalyzer(from_server=False, inp_file="out_list.csv", testing=False, n_test=7)
        for i, k in enumerate(g.prices.keys()):
            g.plot_item_value_to_file(k)
    while True:
        g.daily_update()

    
    

if __name__ == "__main__":
    try:
        reload_all = argv[1] == "server"
        reload_file = argv[1] == "file"
        gp.SERVICE_ACCOUNT_FILE = argv[2]
    except:
        print("Too few and/or wrong arguments!")
        print("Usage:")
        print("python gorilla_analyze.py <server/file> <path_to_service_account_file>")
        print("kkthxbye <3\n")
        exit(1)

    main(reload_server=reload_all, reload_file=reload_file)
