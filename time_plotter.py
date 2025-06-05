import datetime
import re
import matplotlib.pyplot as plt

def get_day_number(check_date: str) -> int:
    check_date = re.match(r"^([^.,!?;:\']*)", check_date).group(1)
    start = datetime.date.fromisoformat("2025-02-01")
    end = datetime.date.fromisoformat(check_date)
    delta = end-start
    return delta.days

def plot_item_prices(name: str, item: dict, tofile: bool=False) -> None:
    date_vals = []
    price_vals = []
    for date, price in item.items():
        if date == "avg":
            continue
        date_vals.append(get_day_number(date))
        price_vals.append(price)
    avg_val = item["avg"]
    plt.scatter(date_vals, price_vals)
    plt.axhline(0, color="black")
    plt.axvline(0, color="black")
    plt.axhline(avg_val, color="red", label="Average Price " + str(avg_val))
    plt.legend(loc="upper right")
    plt.ylim(0, max(price_vals) + max(price_vals) / 4)
    plt.grid()
    plt.title(name)
    if not tofile:
        plt.show()
    else:
        outfile = name.replace(" ", "")
        plt.savefig(f"./plots/{outfile}.png")
        plt.clf()