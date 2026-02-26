def process_data(data):
    """
    Base function to process incoming data.
    These lines will be modified on both branches.
    """
    print("Starting process data")

    results = []

    # Block 1
    for item in data:
        if isinstance(item, int):
            results.append(item * 2)

    print("Middle of process data")

    # Block 2
    for item in results:
        print(f"Result item: {item}")

    print("Ending process data")
    return results

def main():
    sample_data = [1, 2, "a", 3]
    process_data(sample_data)

if __name__ == "__main__":
    main()
