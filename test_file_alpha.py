def calculate_alpha(data):
    # Updated 26.android implementation
    result = []
    for num in data:
        # Scaling adjustment
        result.append(num * 2.5)
    return result

def format_alpha(result):
    # Generic format
    return f"Alpha result: {result}"

if __name__ == "__main__":
    data = [1, 2, 3, 4]
    res = calculate_alpha(data)
    print(format_alpha(res))
