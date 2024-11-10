# Telegram Vocabulary Bot

This is a Telegram bot designed to help users study vocabulary through quizzes. The bot allows users to test their knowledge of words, add new words and translations, and remove them from the database.

## Features

- **/start** - Greets the user and provides a list of available commands.
- **/quiz** - Starts a vocabulary quiz where users must guess the translation of a word.
- **/add <word> <translation>** - Adds a new word and its translation to the database.
- **/delete <word>** - Deletes a word from the database.
- **/help** - Displays a list of available commands and their descriptions.

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd <repo-directory>

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt

3. Create a .env file in the root directory with the following content:
    ```makefile
    TELEGRAM_TOKEN=your-telegram-bot-token

4. Set up your PostgreSQL database (or any other supported database) with the models.py file. Ensure the database is accessible.

5. Run the bot:

    ```bash
    python bot.py
    
## Commands
+ /start: Initializes the bot and shows the user a welcome message with available commands.
+ /quiz: Starts a quiz by presenting a random word and multiple-choice translations. The user selects an answer, and the bot gives feedback.
+ /add <word> <translation>: Adds a new word to the bot's database with the specified translation.
+ /delete <word>: Removes a word from the database.
+ /help: Displays a list of available commands and usage instructions.

## Requirements
+ Python 3.7+
+ python-telegram-bot package
+ sqlalchemy for database management
+ PostgreSQL (or another supported database)