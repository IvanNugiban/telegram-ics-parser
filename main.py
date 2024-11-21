from icalendar import Calendar
import recurring_ical_events
from src.constants import TABLE_WIDTH, TABLE_HEIGHT
from src.scheduler import Scheduler
from src.database import Database
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from src.utils import (
    clamp_text,
    col_num_to_symbols,
    index_to_color,
    event_to_rows,
    event_duration,
    remove_file,
    is_valid_time_format)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
    Application,
    CallbackQueryHandler,
    CallbackContext,

)
import os
import datetime

database = Database()

# States for the file conversation
WAITING_FOR_NAME, WAITING_FOR_FILE = range(2)

# Temporary storage for data
user_data = {}

commands = [
    ('add', 'Add a new ics file'),
    ('show', 'Show an image of the table'),
    ('files', 'Show all files'),
    ('schedule', 'Schedule a showing of the table'),
    ('cancel_schedule', 'Cancel the schedule')
]

async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(commands)

# Command to start the "add" process
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if len(database.get_files(update.message.chat_id)) >= 6:
        await update.message.reply_text("You have reached the limit of tables.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Cancel", callback_data='cancel')],
    ]

    await update.message.reply_text("Please enter the name of person:", reply_markup=InlineKeyboardMarkup(keyboard))
    return WAITING_FOR_NAME

# Save the name and prompt for the file
async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['name'] = update.message.text

    if database.get_row(update.message.chat_id, user_data['name']):
        await update.message.reply_text("Table with this name already exists.")
        return WAITING_FOR_NAME

    keyboard = [
        [InlineKeyboardButton("Cancel", callback_data='cancel')],
    ]

    await update.message.reply_text("Great! Now please send the ics table:", reply_markup=InlineKeyboardMarkup(keyboard))
    return WAITING_FOR_FILE

# Save the file and complete the process
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    document = update.message.document
    chat_id = update.message.chat_id
    username = user_data['name']

    if not document or not document.file_name.endswith(".ics"):
        await update.message.reply_text("Please send a valid file.")
        return WAITING_FOR_FILE

    # Download the file
    file_id = document.file_id
    new_file = await context.bot.get_file(file_id)

    file_path = 'static/' + f"{username}_{document.file_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"  # Construct a unique file name
    os.makedirs('static', exist_ok=True)
    await new_file.download_to_drive(file_path)

    # Create a table for the chat if it doesn't exist and add the file
    database.create_chat_table(chat_id)
    database.add_file(chat_id, username, file_path)

    await update.message.reply_text(
        f"Table '{document.file_name}' has been successfully saved for '{username}'!")
    user_data.clear()  # Clear temporary data
    return ConversationHandler.END

# Cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

async def cancel_callback(update: Update, context: CallbackContext) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="Operation canceled.")
    return ConversationHandler.END

async def create_table(chat_id, context, days):
    columns = database.get_files(chat_id)

    if len(columns) == 0:
        await context.bot.send_message(chat_id, "No files to parse.")
        return False

    if len(columns) > 6:
        await context.bot.send_message(chat_id, "Too many tables selected")
        return False

    events_exist, events = get_events_for_day(columns, days)

    if not events_exist:
        await context.bot.send_message(chat_id, "No events found for that day.")
        return False

    rows = ['', '8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00',
            '19:00', '20:00', '21:00']
    scheduler = Scheduler(TABLE_WIDTH, TABLE_HEIGHT, len(rows), len(columns) + 1)

    for row in rows:
        scheduler.write_text(0, rows.index(row), rows.index(row), row, font_size=14)

    for index, column in enumerate(columns):
        scheduler.write_text(index + 1, 0, 0, column['name'], font_size=14)

        for event in events[column['name']]:
            start_row, end_row = event_to_rows(event['start'], event['end'])
            scheduler.draw_block(index + 1, start_row[0], end_row[0], index_to_color(index), start_row[1], end_row[1])
            scheduler.write_text(index + 1, start_row[0], end_row[0],
                                 event['text'], color='white', font_size=12, font="resources/ariblk.ttf",
                                 align_x='left', align_y='top',
                                 start_row_multiplier=start_row[1], end_row_multiplier=end_row[1])

            if event_duration(event['start'], event['end']) > 60:
                scheduler.write_text(index + 1, start_row[0], end_row[0],
                                     event['from_to'], color='white', font_size=12, font="resources/ariblk.ttf",
                                     align_x='left', align_y='center',
                                     start_row_multiplier=start_row[1], end_row_multiplier=end_row[1])

    scheduler.save("output.png")
    return True

def get_events_for_day(columns, day = 0):
    tomorrow = datetime.date.today() + datetime.timedelta(days=day)
    events = {}
    events_exist = False

    for table in columns:
        with open(table['file'], 'rb') as f:
            table['file'] = Calendar.from_ical(f.read())

        name = table['name']
        if name not in events:
            events[name] = []

        for event in recurring_ical_events.of(table['file']).at(tomorrow):
            events_exist = True
            event_summary = event.get("summary")
            event_start = event.get("dtstart").dt
            event_end = event.get("dtend").dt

            events[name].append({
                "start": event_start,
                "end": event_end,
                'from_to': f"{event_start.strftime('%H:%M')} - {event_end.strftime('%H:%M')}",
                "text": clamp_text(event_summary, col_num_to_symbols(len(columns)))
            })

    return events_exist, events

async def show_table(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    days = int(context.args[0]) if context.args and context.args[0].isdigit() else 0
    if await create_table(update.message.chat_id, context, days):
        await update.message.reply_photo(open("output.png", "rb"))

async def show_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    columns = database.get_files(update.message.chat_id)

    if len(columns) == 0:
        await update.message.reply_text("No files to show.")
        return

    keyboard = []

    for column in columns:
        keyboard.append([InlineKeyboardButton(column['name'], callback_data=f'remove_{column["name"]}')])

    await update.message.reply_text('Your files (click to remove):', reply_markup=InlineKeyboardMarkup(keyboard))

async def remove_callback(update: Update, context: CallbackContext) -> None:
    await update.callback_query.answer()
    name = update.callback_query.data.split('_')[1]
    chat_id = update.callback_query.message.chat.id
    columns = database.get_files(chat_id)

    if name not in [column['name'] for column in columns]:
        await update.callback_query.edit_message_text("File not found.")
        return

    # Remove file from db and static folder
    remove_file(database.get_row(chat_id, name)[2])
    database.remove_row(chat_id, name)

    await update.callback_query.edit_message_text(f"Table '{name}' has been removed.")

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    arguments = context.args

    # Check if arguments valid
    if len(arguments) != 2 or not is_valid_time_format(arguments[0]) \
    or not arguments[1].isdigit() or int(arguments[1]) < 0:
        await update.message.reply_text(
            "Use this format to create schedule:\n\n"
            "/schedule time days_ahead\n\n"
            "'Time' should be in the exact format HH:MM (24-hour format).\n\n"
            "'Days ahead' is how much days ahead ics table should be."
        )
        return

    time = arguments[0]
    days_ahead = int(arguments[1])

    # Add new task to database
    database.add_schedule(update.message.chat_id, time, days_ahead)

    await update.message.reply_text(f"Table will be shown at {time} each day, {days_ahead} days ahead.")

async def show_scheduled_table(context: CallbackContext) -> None:
    schedules = database.get_schedules()

    for schedule in schedules:
        hours = int(schedule[1].split(':')[0])
        minutes = int(schedule[1].split(':')[1])

        if datetime.datetime.now().hour == hours and datetime.datetime.now().minute == minutes:
            if await create_table(schedule[0], context, int(schedule[2])):
                await context.bot.send_photo(photo=open("output.png", "rb"), chat_id=schedule[0])

async def cancel_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if database.get_schedule(update.message.chat_id):
        database.remove_schedule(update.message.chat_id)
        await update.message.reply_text("Schedule has been removed.")

    else:
        await update.message.reply_text("No schedule found.")


def main():

    # Initialize db
    database.connect()
    database.create_schedule_table()

    # Initialize the bot
    bot_token = os.getenv("bot_token")
    app = ApplicationBuilder().token(bot_token).post_init(post_init).build()

    job_queue = app.job_queue
    job_queue.run_repeating(show_scheduled_table, interval=60, first=0)

    # Add handlers
    app.add_handler(CommandHandler("show", show_table))
    app.add_handler(CommandHandler("files", show_files))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("cancel_schedule", cancel_schedule))

    app.add_handler(CallbackQueryHandler(remove_callback, pattern='^remove_.*$'))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', start_add)],
        states={
            WAITING_FOR_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_name),
                CallbackQueryHandler(cancel_callback, pattern='^cancel$'),
            ],
            WAITING_FOR_FILE: [
                MessageHandler(~filters.COMMAND, save_file),
                CallbackQueryHandler(cancel_callback, pattern='^cancel$')
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel),
                   MessageHandler(filters.COMMAND, cancel)],
    )

    app.add_handler(conv_handler)
    # Start the bot
    app.run_polling()
    # Close the database connection
    database.close()

# add action to schedule
# add requirements.txt

if __name__ == "__main__":
    load_dotenv()
    main()


