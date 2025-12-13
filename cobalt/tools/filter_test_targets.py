import argparse
import json
import os
import glob
import sys

import junit_mini_parser

def get_target_name(target, mode):
    if mode == 'device':
        # "path/to:target_name" -> "target_name"
        if ':' in target:
            return target.split(':')[-1]
        return target
    elif mode == 'host':
        # "out/dir/target_binary" -> "target_binary"
        return os.path.splitext(os.path.basename(target))[0]
    return target

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--targets', required=True)
    parser.add_argument('--results-dir', required=True)
    parser.add_argument('--mode', choices=['device', 'host'], required=True)
    args = parser.parse_args()

    try:
        targets = json.loads(args.targets)
    except:
        print("Invalid targets JSON", file=sys.stderr)
        sys.exit(1)

    filtered = []

    # If results dir doesn't exist, it means download failed or no previous results.
    # We should re-run everything.
    if not os.path.exists(args.results_dir):
        print(json.dumps(targets))
        return

    for target in targets:
        name = get_target_name(target, args.mode)

        xml_files = []
        if args.mode == 'device':
             # device XMLs are deep: dir/subdir/target_testoutput.xml
             pattern = os.path.join(args.results_dir, '**', f'{name}_testoutput.xml')
             xml_files = glob.glob(pattern, recursive=True)
        else:
             # Host XMLs: target_result.xml
             pattern = os.path.join(args.results_dir, '**', f'{name}_result.xml')
             xml_files = glob.glob(pattern, recursive=True)

        if not xml_files:
            print(f"Missing XML for {name}, adding to retry.", file=sys.stderr)
            filtered.append(target)
            continue

        # Use parser to detect failures
        failing_tests = junit_mini_parser.find_failing_tests(xml_files)

        if failing_tests:
            print(f"Found failures for {name}.", file=sys.stderr)
            filtered.append(target)
        else:
            print(f"{name} passed previously.", file=sys.stderr)

    print(json.dumps(filtered))

if __name__ == '__main__':
    main()
