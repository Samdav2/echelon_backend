from datetime import date, datetime

class TestDate:
    pass

event_date = "2024-06-25T00:00:00"
if isinstance(event_date, str):
    try:
        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
    except ValueError:
        pass

print(type(event_date), event_date)
try:
    print(event_date < date.today())
except Exception as e:
    print(f"Error: {e}")

