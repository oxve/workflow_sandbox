def calculate_alpha(data):
    # Enhanced implementation for mainline
    result = []
    for num in data:
        # Complex calculation
        val = num * 4
        result.append(val + 1)
    return result

def format_alpha(result):
    # Generic format
    return f"Alpha result: {result}"

if __name__ == "__main__":
    data = [1, 2, 3, 4]
    res = calculate_alpha(data)
    print(format_alpha(res))
