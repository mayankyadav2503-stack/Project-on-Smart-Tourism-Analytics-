import sqlite3
from datetime import datetime
from config import DB_PATH

def get_currency_rates(base="USD"):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT target_currency, rate FROM currency_rates WHERE base_currency=?", (base,))
    rows = cur.fetchall()
    conn.close()
    return {row["target_currency"]: row["rate"] for row in rows}

def convert_currency(amount, from_cur, to_cur):
    if from_cur == to_cur:
        return amount
    rates = get_currency_rates(from_cur)
    if to_cur in rates:
        return round(amount * rates[to_cur], 2)
    rates_from = get_currency_rates("USD")
    if from_cur in rates_from and to_cur in rates_from:
        usd_amount = amount / rates_from[from_cur]
        return round(usd_amount * rates_from[to_cur], 2)
    return amount
