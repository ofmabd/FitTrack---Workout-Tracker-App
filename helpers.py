from datetime import datetime

def format_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return date_string


