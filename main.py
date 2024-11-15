from icalendar import Calendar
import recurring_ical_events
from src.constants import TABLE_WIDTH, TABLE_HEIGHT
from src.scheduler import Scheduler
from src.utils import clamp_text, col_num_to_symbols, index_to_color, event_to_rows, event_duration
from src.database import Database
import datetime

def main():

    # Connect to db
    database = Database()
    database.connect()
    database.create_tables()

    columns = database.get_files()

    if len(columns) == 0:
        print("No tables selected")
        return

    if len(columns) > 6:
        print("Too many tables selected")
        return

    for table in columns:
        with open(table['file'], 'rb') as f:
            table['file'] = Calendar.from_ical(f.read())

    tomorrow = datetime.date.today() + datetime.timedelta(days=0)
    events = {}

    for table in columns:

        name = table['name']

        if name not in events:
            events[name] = []

        # Collect all events for tomorrow
        for event in recurring_ical_events.of(table['file']).at(tomorrow):
            event_summary = event.get("summary")
            event_start = event.get("dtstart").dt
            event_end = event.get("dtend").dt

            events[name].append({
                "start" : event_start,
                "end" : event_end,
                'from_to': f"{event_start.strftime('%H:%M')} - {event_end.strftime('%H:%M')}",
                "text" : clamp_text(event_summary, col_num_to_symbols(len(columns)))
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

            # Don't print time for events shorter than 1 hour
            if event_duration(event['start'], event['end']) > 60:
                scheduler.write_text(index + 1, start_row[0], end_row[0],
                                 event['from_to'], color='white', font_size=12, font="ariblk.ttf",
                                 align_x='left', align_y='center',
                                 start_row_multiplier=start_row[1], end_row_multiplier=end_row[1])

    database.close()
    scheduler.show()
    scheduler.save("output.png")

if __name__ == "__main__":
    main()
