#!/usr/bin/env python3
import os
import argparse
import subprocess
import ast
import json

def get_conflict_files(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(os.path.join(root, filename))
    return files

def evaluate_files(files):
    stats = {
        "total_files": len(files),
        "files_with_markers": 0,
        "valid_python": 0,
        "invalid_python": 0,
        "errors": []
    }

    for filepath in files:
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Check for leftover conflict markers
            if '<<<<<<<' in content or '=======' in content or '>>>>>>>' in content:
                stats["files_with_markers"] += 1
                stats["errors"].append(f"Leftover markers in {filepath}")
                continue # If it has markers, it's definitely invalid

            # Check for valid Python syntax
            try:
                ast.parse(content)
                stats["valid_python"] += 1
            except SyntaxError as e:
                stats["invalid_python"] += 1
                stats["errors"].append(f"Syntax error in {filepath}: {e}")

        except Exception as e:
            stats["errors"].append(f"Error processing {filepath}: {e}")

    return stats

def main():
    parser = argparse.ArgumentParser(description="Evaluate Gemini Conflict Resolver")
    parser.add_argument("--test-dir", type=str, required=True, help="Directory containing conflict files")
    parser.add_argument("--resolver-script", type=str, default=".github/scripts/gemini_conflict_resolver.py", help="Path to resolver script")

    args = parser.parse_args()

    if not os.path.exists(args.test_dir):
        print(f"Test directory not found: {args.test_dir}")
        return

    conflict_files = get_conflict_files(args.test_dir)
    print(f"Found {len(conflict_files)} test files.")

    if not conflict_files:
        print("No Python files found in test directory.")
        return

    # Run resolver
    print(f"Running resolver on {len(conflict_files)} files in batches of 20...")

    batch_size = 20
    for i in range(0, len(conflict_files), batch_size):
        batch = conflict_files[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(conflict_files) - 1)//batch_size + 1} ({len(batch)} files)...")
        resolver_cmd = ["python3", args.resolver_script] + batch

        try:
            env = os.environ.copy()
            result = subprocess.run(resolver_cmd, capture_output=True, text=True, env=env)
            if result.returncode != 0:
                print(f"Warning: Resolver script batch {i//batch_size + 1} exited with code {result.returncode}")
                print(f"Stdout:\n{result.stdout}")
                print(f"Stderr:\n{result.stderr}")
            else:
                # If the script prints warning messages but exits 0
                if "Failed to get resolutions" in result.stdout or "Error" in result.stdout:
                    print(f"Batch {i//batch_size + 1} finished with warnings:")
                    print(f"Stdout:\n{result.stdout}")
                    print(f"Stderr:\n{result.stderr}")
                else:
                    print(f"Batch {i//batch_size + 1} completed successfully.")
        except Exception as e:
            print(f"Error running resolver on batch {i//batch_size + 1}: {e}")
            return

    # Evaluate Results
    print("Evaluating resolved files...")
    stats = evaluate_files(conflict_files)

    print("\n--- Evaluation Results ---")
    print(f"Total Files: {stats['total_files']}")
    print(f"Successfully Resolved (Valid Syntax): {stats['valid_python']}")
    print(f"Invalid Syntax: {stats['invalid_python']}")
    print(f"Leftover Conflict Markers: {stats['files_with_markers']}")

    success_rate = (stats['valid_python'] / stats['total_files']) * 100 if stats['total_files'] > 0 else 0
    print(f"Success Rate: {success_rate:.2f}%")

    if stats["errors"]:
        print("\nErrors/Issues:")
        for err in stats["errors"][:10]: # Print top 10 errors
            print(f" - {err}")
        if len(stats["errors"]) > 10:
            print(f" - ... and {len(stats['errors']) - 10} more.")

if __name__ == "__main__":
    main()
