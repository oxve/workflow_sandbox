<<<<<<< HEAD
def process_data(data, enable_advanced_filter=False):
    """
    Modified Android version of process data.
    Added a flag for advanced filtering in older versions.
    """
    import logging
    logging.info("Starting process data on Android 26 branch")

    results = []

    # Block 1 - Legacy string conversion before int check
    for item in data:
        if type(item) is str and item.isdigit():
            item = int(item)

        if isinstance(item, int):
            if enable_advanced_filter and item < 0:
                 continue
            results.append(item * 3) # Note: Android multiplier is 3

    logging.debug("Middle of process data - filtering complete")
=======
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
>>>>>>> 2b2510d (Merge pull request #19 from oxve/feature/gemini-complex-conflict-6)

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
