import time

def add(x, y):
    """Adds two numbers and returns the result."""
    return x + y

def greet(name):
    """Greets the user with a personalized message, sanitizing the input."""
    sanitized_name = "".join(char for char in name if char.isalnum())
    return "Hello, " + sanitized_name + "!"

def slow_function():
    """A function that simulates a slow operation."""
    # time.sleep(1) # Removed to improve performance
    return "Done"