def process_data(data, enable_tracing=True, scale_factor=2):
    """
    Modern version of process data for the main branch.
    Supports comprehensive tracing and dynamic scaling.
    """
    if enable_tracing:
        print("TRACE: Starting process data on main branch")

    results = []

    # Block 1 - Refactored type-safe processing
    results = [
        item * scale_factor for item in data
        if isinstance(item, int) and item % 2 == 0 # Only process even integers
    ]

    if enable_tracing:
        print(f"TRACE: Middle of process data, found {len(results)} valid items")

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
