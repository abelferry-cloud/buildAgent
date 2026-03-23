def greet(name):
    """Return a greeting message.
    
    Args:
        name (str): The name of the person to greet.
        
    Returns:
        str: A greeting message in the format "Hello, {name}!"
        
    Examples:
        >>> greet("Alice")
        'Hello, Alice!'
        >>> greet("World")
        'Hello, World!'
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Example usage
    print(greet("World"))