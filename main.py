import re  # Regular expression library
import random
import requests


def get_joke():
    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,explicit&format=txt"
    response = requests.get(url)
    return response.text


def handle_name(user_input):
    global user_name
    if "my name is " in user_input:
        user_name = user_input.split("my name is ")[-1].strip()
        return f"Got it, {user_name}!"
    elif "i am " in user_input:
        user_name = user_input.split("i am ")[-1].strip()
        return f"Got it, {user_name}!"
    elif "call me " in user_input:
        user_name = user_input.split("call me ")[-1].strip()
        return f"Got it, {user_name}!"
    else:
        return "I'm sorry, I didn't catch your name. Can you please tell me again?"


def handle_calculator(user_input):
    # Extract numbers from user input
    numbers = re.findall(r"\d+", user_input)
    if len(numbers) < 2:
        return "Please provide two numbers for calculation."

    # Extract operator from user input
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

    # Perform calculation
    number1, number2 = map(float, numbers)
    if operator == "+":
        return f"The result is {number1 + number2}."
    elif operator == "-":
        return f"The result is {number1 - number2}."
    elif operator == "*":
        return f"The result is {number1 * number2}."
    elif operator == "/":
        if number2 == 0:
            return "Cannot divide by zero."
        return f"The result is {number1 / number2}."


response = {
    "hi": "Hello, how can I help you?",
    "hello": "Hello, how can I help you?",
    "hey": "Hello, how can I help you?",
    "how are you": "I'm fine, thank you. How can I help you?",
    "what is your name": "My name is JellyBean. How can I help you?",
    "who are you": "I'm JellyBean. How can I help you?",
    "what can you do": "I can help you with your queries. How can I help you?",
    "what is your purpose": "I can help you with your queries. How can I help you?",
    "what are you": "I'm JellyBean. How can I help you?",
    "what is your function": "I can help you with your queries. How can I help you?",
    "what is your job": "I can help you with your queries. How can I help you?",
    "what is your role": "I can help you with your queries. How can I help you?",
    "what can you do?": "I can do basic calculations and I can chat with you. How can I help you?",
    "bye": "Goodbye! Have a great day!",
    "goodbye": "Goodbye! Have a great day!",
    "see you": "Goodbye! Have a great day!",
    "later": "Goodbye! Have a great day!",
    "exit": "Goodbye! Have a great day!",
    "quit": "Goodbye! Have a great day!",
    "thanks": "You're welcome!",
    "thank you": "You're welcome!",
    "ok": "Alright!",
    "okay": "Alright!",
    "alright": "Alright!",
    "yes": "Alright!",
    "no": "Alright!",
    "sure": "Alright!",
    "maybe": "Alright!",

}


def main():
    print("JellyBean: Hello, how can I help you?")
    while True:
        user_input = input("You: ").lower()

        # Use regex to find matching responses
        matched = False
        for key in response:
            # Word boundary for better matching
            if re.search(r"\b" + re.escape(key) + r"\b", user_input):
                print("JellyBean:", response[key])
                matched = True
                break
            elif "calculate" in user_input:
                result = handle_calculator(user_input)
                print("JellyBean:", result)
                matched = True
                break
            elif "my name is " in user_input or "i am " in user_input or "call me " in user_input:
                result = handle_name(user_input)
                print("JellyBean:", result)
                matched = True
                break
            elif "joke" in user_input:
                joke = get_joke()
                print("JellyBean:", joke)
                matched = True
                break

        if not matched:
            print("JellyBean: Sorry, I don't understand. Can you please rephrase?")


if __name__ == "__main__":
    main()
