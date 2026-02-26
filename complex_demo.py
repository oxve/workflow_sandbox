def process_data(data, enable_advanced_filter=False, enable_tracing=True, scale_factor=3):
    """
    Combined version of process data for both Android and main.
    Supports advanced filtering, comprehensive tracing, and dynamic scaling.
    """
    import logging

    if enable_tracing:
        logging.info("TRACE: Starting process data")

    results = []

    # Combined processing loop
    for item in data:
        # From HEAD: Legacy string conversion
        if type(item) is str and item.isdigit():
            item = int(item)

        # Check if item is an integer and passes all filters
        if isinstance(item, int):
            # From HEAD: Advanced filter for negative numbers
            if enable_advanced_filter and item < 0:
                continue
            
            # From Incoming: Only process even integers
            if item % 2 != 0:
                continue

            # Apply scaling, using Android's multiplier as the default
            results.append(item * scale_factor)

    if enable_tracing:
        logging.debug(f"TRACE: Middle of process data, found {len(results)} valid items")

    return results

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
