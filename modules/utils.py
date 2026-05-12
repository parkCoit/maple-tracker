from datetime import datetime, timedelta

def format_korean_currency(value):
    if value >= 10000:
        eok = int(value // 10000)
        man = int(value % 10000)
        if man == 0:
            return f"{eok}억"
        return f"{eok}억 {man:,}만"
    return f"{int(value):,}" if value > 0 else "0"

def get_week_of_month(dt):
    first_day = dt.replace(day=1)
    dom = dt.day
    adjusted_dom = dom + first_day.weekday()
    return (adjusted_dom - 1) // 7 + 1

def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)