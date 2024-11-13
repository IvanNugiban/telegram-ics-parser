from icalendar import Calendar
import recurring_ical_events
import datetime
from src.constants import TABLE_WIDTH, TABLE_HEIGHT, MAX_SYMBOLS
from src.scheduler import Scheduler

def index_to_color(index):
    colors = ['#333333', '#000080', '#DC143C', '#228B22', '#4B0082', '#FF4500']
    return colors[index % len(colors)]

def time_to_row(time, rows):
    time_mapping = {
        '8AM': 1, '9AM': 2, '10AM': 3, '11AM': 4, '12PM': 5,
        '1PM': 6, '2PM': 7, '3PM': 8, '4PM': 9, '5PM': 10,
        '6PM': 11, '7PM': 12, '8PM': 13, '9PM': 14
    }
    time_str = time.strftime('%I%p').lstrip('0').upper()
    time_percentage = time.minute / 60
    return time_mapping.get(time_str, None), time_percentage

def event_to_rows(event_start, event_end, rows):
    start_row = time_to_row(event_start, rows)
    end_row = time_to_row(event_end, rows)
    return start_row, end_row

def clamp_text(text):
    if len(text) > MAX_SYMBOLS:
        return text[:MAX_SYMBOLS] + "..."
    return text

def main():

    columns = [
        {"file": "C:/Users/Ivan/Downloads/Plany.ics", "name": "Ivan"},
        {"file": "C:/Users/Ivan/Downloads/kolya.ics", "name": "Mykola"},
        {"file": "C:/Users/Ivan/Downloads/valeria.ics", "name": "Valera"},
    ]

    if len(columns) == 0:
        print("No tables selected")
        return

    if len(columns) > 6:
        print("Too many tables selected")
        return

    for table in columns:
        with open(table['file'], 'rb') as f:
            table['file'] = Calendar.from_ical(f.read())

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    events = {}

    for table in columns:
        # Collect all events for tomorrow
        for event in recurring_ical_events.of(table['file']).at(tomorrow):
            event_summary = event.get("summary")
            event_start = event.get("dtstart").dt
            event_end = event.get("dtend").dt

            name = table['name']

            if name not in events:
                events[name] = []

            events[name].append({
                "start" : event_start,
                "end" : event_end,
                'from_to': f"{event_start.strftime('%H:%M')} - {event_end.strftime('%H:%M')}",
                "text" : clamp_text(event_summary)
            })

    # Rows  (first row  is empty)
    rows = ['', '8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']
    # Add 1 in columns for empty space
    scheduler = Scheduler(TABLE_WIDTH, TABLE_HEIGHT, len(rows), len(columns) + 1)

    # Draw time slots
    for row in rows:
        scheduler.write_text( 0, rows.index(row), rows.index(row), row, font_size=14)

    for index, column in enumerate(columns):
        # Draw names, skip first column
        scheduler.write_text( index + 1, 0, 0, column['name'], font_size=14)

        for event in events[column['name']]:
            start_row, end_row = event_to_rows(event['start'], event['end'], len(rows))
            # Draw events blocks
            scheduler.draw_block(index + 1, start_row[0], end_row[0], index_to_color(index), start_row[1], end_row[1])
            # Draw text for events
            scheduler.write_text(index + 1, start_row[0], end_row[0],
                                 event['text'], color='white', font_size=12, font="ariblk.ttf",
                                 align_x='left', align_y='top',
                                 start_row_multiplier=start_row[1], end_row_multiplier=end_row[1])

            scheduler.write_text(index + 1, start_row[0], end_row[0],
                                 event['from_to'], color='white', font_size=12, font="ariblk.ttf",
                                 align_x='left', align_y='center',
                                 start_row_multiplier=start_row[1], end_row_multiplier=end_row[1])

    scheduler.show()
    scheduler.save("output.png")

if __name__ == "__main__":
    main()
