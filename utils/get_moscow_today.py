from datetime import datetime
import pytz

def get_moscow_today():
    return datetime.now(pytz.timezone("Europe/Moscow")).date()