def calculate_alpha(data):
    # Enhanced 26.android implementation
    result = []
    for num in data:
        # Complex calculation with scaling adjustment
        val = num * 5.0
        result.append(val + 1)
    return result

def format_alpha(result):
    # Generic format
    return f"Alpha result: {result}"

if __name__ == "__main__":
    data = [1, 2, 3, 4]
    res = calculate_alpha(data)
    print(format_alpha(res))
