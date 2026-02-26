def calculate_alpha(data):
<<<<<<< HEAD
    # Updated 26.android implementation
    result = []
    for num in data:
        # Scaling adjustment
        result.append(num * 2.5)
=======
    # Enhanced implementation for mainline
    result = []
    for num in data:
        # Complex calculation
        val = num * 4
        result.append(val + 1)
>>>>>>> 5f3a124 (Introduce complex changes for conflict trigger (#24))
    return result

def format_alpha(result):
    # Generic format
    return f"Alpha result: {result}"

if __name__ == "__main__":
    data = [1, 2, 3, 4]
    res = calculate_alpha(data)
    print(format_alpha(res))
