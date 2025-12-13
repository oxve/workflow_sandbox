#!/usr/bin/env python3
#
# Copyright 2025 The Cobalt Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Generates filters from local test results."""

import argparse
import json
import os

import junit_mini_parser


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input-dir',
      required=True,
      help='Directory containing extracted test artifacts.')
  parser.add_argument(
      '--filter-out-dir', required=True, help='Directory to output filter files.')
  args = parser.parse_args()

  xml_files = []
  for root, _, files in os.walk(args.input_dir):
    for f in files:
      if f.endswith('.xml'):
        xml_files.append(os.path.join(root, f))

  if not xml_files:
    print(f'No XML files found in {args.input_dir}.')
    return

  failing_tests = junit_mini_parser.find_failing_tests(xml_files)

  target_failures = {}

  for rel_path, failures in failing_tests.items():
    filename = os.path.basename(rel_path)
    if filename.endswith('_result.xml'):
      target = filename[:-11]
    elif filename.endswith('_testoutput.xml'):
      target = filename[:-15]
    else:
      target = filename.replace('.xml', '')

    # Test names are stored as tuple (test_name, message) in failing_tests
    # We need the first element.
    test_names = [t[0] for t in failures]

    if target not in target_failures:
      target_failures[target] = []
    target_failures[target].extend(test_names)

  os.makedirs(args.filter_out_dir, exist_ok=True)

  for target, tests in target_failures.items():
    filter_data = {'failing_tests': tests}
    with open(
        os.path.join(args.filter_out_dir, f'{target}_filter.json'),
        'w',
        encoding='utf-8') as f:
      json.dump(filter_data, f, indent=2)
    print(f'Wrote filter for {target} with {len(tests)} failures.')

  print('FAILED_TARGETS=' + ' '.join(target_failures.keys()))


if __name__ == '__main__':
  main()