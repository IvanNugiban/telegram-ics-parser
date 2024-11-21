# Telegram ics parser bot

This project is a Telegram bot that allows users to manage and schedule events using `.ics` files. The bot can display schedules, manage files, and set up recurring schedules.

![Example](resources/schedule_example.jpeg)

## Features

- Display schedules for a specified number of days ahead.
- Manage `.ics` files (add, remove, list).
- Set up recurring schedules to automatically send schedules at specified times.
- Handle errors gracefully.

## Requirements

- Python 3.10 or higher
- `pip` for managing Python packages

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/IvanNugiban/your-repo.git
    cd your-repo
    ```

2. Create a virtual environment and activate it:

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    Create a `.env` file in the project directory and add your bot token:

    ```sh
    echo "bot_token=YOUR_BOT_TOKEN" > .env
    ```

## Usage

1. Run the bot:

    ```sh
    python main.py
    ```

2. Interact with the bot on Telegram:
    - Use `/add` to add a file (up to 6). 
    - Use `/show` to display the schedule for today.
    - Use `/files` to list all managed files.
    - Use `/schedule time days_ahead` to set up a recurring schedule.
    - Use `/cancel_schedule` to cancel the recurring schedule.

## Usage without telegram

If you want to just create table without using telegram, please clone 
commmit `391f568` and run `python main.py` to create table.

## Contributing

Feel free to submit issues or pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License.
```

Replace `YOUR_BOT_TOKEN` and `your-repo` with your actual bot token and repository name.