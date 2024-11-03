import tkinter as tk
from icalendar import Calendar, Event
import recurring_ical_events
import datetime
from src.constants import TABLE_WIDTH, TABLE_HEIGHT
from src.scheduler import Scheduler


def main():

    # Initialize tkinter for file dialogs
    root = tk.Tk()
    root.withdraw()

    # table = choose_file("ics")
    ics = "C:/Users/Ivan/Downloads/Plany.ics"

    if not ics:
        return

    with open(ics, 'rb') as f:
        ics = Calendar.from_ical(f.read())

    today = datetime.date.today()
    events_by_date = {}

    for event in recurring_ical_events.of(ics).at(today):
        event_summary = event.get("summary")
        event_start = event.get("dtstart").dt

    # Rows and columns (first row and column is empty)
    rows = ["", '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM']
    columns = ["", 'Ivan', 'Serhii', 'Dima', 'Drake', 'John']

    scheduler = Scheduler(TABLE_WIDTH, TABLE_HEIGHT, len(rows), len(columns))

    for row in rows:
        scheduler.write_text(rows.index(row), 0, row)

    for column in columns:
        scheduler.write_text(0, columns.index(column), column)

    scheduler.show()

if __name__ == "__main__":
    main()
