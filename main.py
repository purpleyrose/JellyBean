import re  # Regular expression library
import random
import requests
import sqlite3
import time
import threading
from datetime import datetime

# Database initialization


def initialize_database():
    conn = sqlite3.connect("jellybean.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    # Create reminders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            remind_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

# User management


def get_or_create_user(name):
    conn = sqlite3.connect("jellybean.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
    else:
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        user_id = cursor.lastrowid
        conn.commit()

    conn.close()
    return user_id

# Add a reminder


def add_reminder(user_id, message, delay_seconds):
    conn = sqlite3.connect("jellybean.db")
    cursor = conn.cursor()
    remind_at = datetime.now().timestamp() + delay_seconds
    remind_at_datetime = datetime.fromtimestamp(remind_at)

    cursor.execute("INSERT INTO reminders (user_id, message, remind_at) VALUES (?, ?, ?)",
                   (user_id, message, remind_at_datetime))
    conn.commit()
    conn.close()

    threading.Thread(target=reminder_timer, args=(message, remind_at)).start()

# Reminder timer


def reminder_timer(message, remind_at):
    delay = remind_at - datetime.now().timestamp()
    if delay > 0:
        time.sleep(delay)
    print(f"JellyBean: Reminder - {message}")

# Fetch reminders


def fetch_reminders(user_id):
    conn = sqlite3.connect("jellybean.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT message, remind_at FROM reminders WHERE user_id = ?", (user_id,))
    reminders = cursor.fetchall()
    conn.close()
    return reminders

# Delete a reminder


def delete_reminder(user_id, message=None):
    conn = sqlite3.connect("jellybean.db")
    cursor = conn.cursor()

    if message:
        # Delete a specific reminder
        cursor.execute(
            "DELETE FROM reminders WHERE user_id = ? AND message = ?", (user_id, message))
        conn.commit()
        if cursor.rowcount > 0:
            result = f"Reminder '{message}' has been deleted."
        else:
            result = f"No reminder found with the message '{message}'."
    else:
        # Delete all reminders for the user
        cursor.execute("DELETE FROM reminders WHERE user_id = ?", (user_id,))
        conn.commit()
        result = "All your reminders have been cleared."

    conn.close()
    return result

# Joke functionality


def get_joke():
    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,explicit&format=txt"
    response = requests.get(url)
    return response.text

# Handle name


def handle_name(user_input):
    if "my name is " in user_input:
        user_name = user_input.split("my name is ")[-1].strip()
        return user_name
    elif "i am " in user_input:
        user_name = user_input.split("i am ")[-1].strip()
        return user_name
    elif "call me " in user_input:
        user_name = user_input.split("call me ")[-1].strip()
        return user_name
    else:
        return None

# Handle calculator


def handle_calculator(user_input):
    numbers = re.findall(r"\d+", user_input)
    if len(numbers) < 2:
        return "Please provide two numbers for calculation."

    operator = None
    if "+" in user_input:
        operator = "+"
    elif "-" in user_input:
        operator = "-"
    elif "*" in user_input:
        operator = "*"
    elif "/" in user_input:
        operator = "/"

    if operator is None:
        return "Please provide a valid operator for calculation."

    number1, number2 = map(float, numbers)
    try:
        return {
            "+": f"The result is {number1 + number2}.",
            "-": f"The result is {number1 - number2}.",
            "*": f"The result is {number1 * number2}.",
            "/": f"The result is {number1 / number2}." if number2 != 0 else "Cannot divide by zero."
        }[operator]
    except KeyError:
        return "Invalid operator."


# Predefined responses
response = {
    "hi": "Hello, how can I help you?",
    "hello": "Hello, how can I help you?",
    "joke": "Sure! Here's one:",
    "bye": "Goodbye! Have a great day!",
}

# Main chatbot logic


def main():
    initialize_database()

    print("JellyBean: Hello! What's your name?")
    user_input = input("You: ").strip()
    user_name = handle_name(user_input) or user_input
    user_id = get_or_create_user(user_name)

    print(f"JellyBean: Hi, {user_name}! How can I help you today?")

    while True:
        user_input = input("You: ").lower()
        matched = False

        if re.match(r"remind me.*in \d+ (seconds?|minutes?|hours?) to .+", user_input):
            try:
                time_match = re.search(
                    r"in (\d+) (seconds?|minutes?|hours?)", user_input)
                message_match = re.search(r"to (.+)", user_input)
                if not time_match or not message_match:
                    raise ValueError("Invalid format for setting reminders.")

                delay = int(time_match.group(1))
                unit = time_match.group(2).lower()
                if "minute" in unit:
                    delay *= 60
                elif "hour" in unit:
                    delay *= 3600

                message = message_match.group(1).strip()
                add_reminder(user_id, message, delay)
                print(
                    f"JellyBean: Reminder set for '{message}' in {delay} seconds.")
            except ValueError as e:
                print(f"JellyBean: {e}")
            matched = True

        elif re.match(r"show reminders", user_input):
            reminders = fetch_reminders(user_id)
            if reminders:
                print("JellyBean: Here are your reminders:")
                for message, remind_at in reminders:
                    friendly_time = datetime.fromtimestamp(
                        remind_at).strftime("%Y-%m-%d %H:%M:%S")
                    print(f" - {message} at {friendly_time}")
            else:
                print("JellyBean: You have no reminders.")
            matched = True

        elif re.match(r"delete all reminders", user_input):
            result = delete_reminder(user_id)
            print(f"JellyBean: {result}")
            matched = True

        elif re.match(r"delete reminder .+", user_input):
            try:
                message = re.search(r"delete reminder (.+)",
                                    user_input).group(1).strip()
                result = delete_reminder(user_id, message)
                print(f"JellyBean: {result}")
            except AttributeError:
                print("JellyBean: Please specify the reminder to delete.")
            matched = True

        elif "joke" in user_input:
            joke = get_joke()
            print("JellyBean:", joke)
            matched = True

        elif "calculate" in user_input:
            result = handle_calculator(user_input)
            print("JellyBean:", result)
            matched = True

        else:
            for key in response:
                if re.search(r"\b" + re.escape(key) + r"\b", user_input):
                    print("JellyBean:", response[key])
                    matched = True
                    break

        if not matched:
            print("JellyBean: Sorry, I don't understand. Can you rephrase?")


if __name__ == "__main__":
    main()
