import datetime
import os

def index_to_color(index):
    colors = ['#333333', '#000080', '#DC143C', '#228B22', '#4B0082', '#FF4500']
    return colors[index % len(colors)]

def time_to_row(time):
    time_mapping = {
        '8AM': 1, '9AM': 2, '10AM': 3, '11AM': 4, '12PM': 5,
        '1PM': 6, '2PM': 7, '3PM': 8, '4PM': 9, '5PM': 10,
        '6PM': 11, '7PM': 12, '8PM': 13, '9PM': 14
    }
    time_str = time.strftime('%I%p').lstrip('0').upper()
    time_percentage = time.minute / 60
    return time_mapping.get(time_str, None), time_percentage

def event_to_rows(event_start, event_end):
    start_row = time_to_row(event_start)
    end_row = time_to_row(event_end)
    return start_row, end_row

def col_num_to_symbols(col_num):
    if col_num == 1:
        return 200
    if col_num == 2:
        return 100
    if col_num == 3:
        return 55
    if col_num == 4:
        return 35
    if col_num == 5:
        return 25
    if col_num == 6:
        return 20

def clamp_text(text, max_symbols):
    if len(text) > max_symbols:
        return text[:max_symbols] + "..."
    return text

def event_duration(start_time: datetime, end_time: datetime) -> float:
    duration = end_time - start_time
    return duration.total_seconds() / 60

def remove_file(path):
    if os.path.exists(path):
        os.remove(path)

def is_valid_time_format(time_str):
    try:
        datetime.datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def format_date_plus_days(days):
    # Get today's date
    today = datetime.datetime.now()
    # Add the specified number of days
    future_date = today + datetime.timedelta(days=days)
    # Format the date as "DD.MM.YYYY"
    return future_date.strftime("%d.%m.%Y")