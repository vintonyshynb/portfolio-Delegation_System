import requests
from decimal import Decimal
from datetime import datetime, timedelta


def get_nbp_rate(currency, date):
    if currency == "PLN":
        return Decimal("1.00")

    dt = datetime.strptime(date, "%Y-%m-%d")

    for _ in range(7):
        try:
            url = f"https://api.nbp.pl/api/exchangerates/rates/A/{currency}/{dt.date()}/?format=json"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return Decimal(str(data["rates"][0]["mid"]))
        except:
            pass
        dt -= timedelta(days=1)

    return Decimal("1.00")
