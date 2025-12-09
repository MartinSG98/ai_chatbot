# Function to reverse a given string

def reverse_string(s: str) -> str:
    """Return the reverse of the input string s."""
    return s[::-1]

# Example usage
if __name__ == "__main__":
    test_str = "hello"
    print(f"Original: {test_str}")
    print(f"Reversed: {reverse_string(test_str)}")
