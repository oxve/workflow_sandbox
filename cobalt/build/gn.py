#!/usr/bin/env python3
import argparse
import os
import json
import sys

def main():
    print(f"Mock gn.py called with args: {sys.argv}")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--platform', required=True)
    parser.add_argument('-C', '--config', required=True)
    args, unknown = parser.parse_known_args()

    out_dir = f"out/{args.platform}_{args.config}"
    os.makedirs(out_dir, exist_ok=True)

    test_targets_file = os.path.join(out_dir, "test_targets.json")
    with open(test_targets_file, 'w') as f:
        json.dump({"test_targets": ["dummy_test"]}, f)

    print(f"Mocked GN gen: Created {test_targets_file}")

if __name__ == "__main__":
    main()
