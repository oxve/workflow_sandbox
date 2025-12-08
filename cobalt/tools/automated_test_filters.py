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
"""Downloads test results from previous attempt and generates filters."""

import argparse
import io
import json
import os
import re
import urllib.error
import urllib.request
import zipfile

import junit_mini_parser


def get_artifacts(repo, run_id, token):
  url = f'https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts'
  headers = {
      'Authorization': f'Bearer {token}',
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
  }
  try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
      data = json.load(response)
      return data.get('artifacts', [])
  except urllib.error.HTTPError as e:
    print(f'Error listing artifacts: {e}')
    return []


def download_artifact(url, token, dest_dir):
  headers = {
      'Authorization': f'Bearer {token}',
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
  }
  try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
      content = response.read()
      with zipfile.ZipFile(io.BytesIO(content)) as z:
        z.extractall(dest_dir)
    return True
  except urllib.error.HTTPError as e:
    print(f'Error downloading artifact: {e}')
    return False
  # pylint: disable=broad-exception-caught
  except Exception as e:
    print(f'Error extracting artifact: {e}')
    return False


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--repo', required=True)
  parser.add_argument('--run-id', required=True)
  parser.add_argument('--token', required=True)
  parser.add_argument('--artifact-pattern', required=True)
  parser.add_argument('--out-dir', required=True)
  parser.add_argument('--filter-out-dir', required=True)
  parser.add_argument('--local-artifacts-dir', help='Local directory to use instead of downloading artifacts.')
  args = parser.parse_args()

  if args.local_artifacts_dir:
    temp_dir = args.local_artifacts_dir
    matched_artifacts = [] # Not used in local mode
  else:
    artifacts = get_artifacts(args.repo, args.run_id, args.token)

    regex = re.compile(args.artifact_pattern)
    matched_artifacts = [a for a in artifacts if regex.match(a['name'])]

    if not matched_artifacts:
      print(f'No artifacts found matching {args.artifact_pattern}')
      return

    temp_dir = args.out_dir
    os.makedirs(temp_dir, exist_ok=True)

  os.makedirs(args.filter_out_dir, exist_ok=True)

  xml_files = []
  if args.local_artifacts_dir:
    for root, _, files in os.walk(temp_dir):
      for f in files:
        if f.endswith('.xml'):
          xml_files.append(os.path.join(root, f))
  else:
    for artifact in matched_artifacts:
      print(f"Downloading artifact: {artifact['name']}")
      if download_artifact(artifact['archive_download_url'], args.token,
                           temp_dir):
        for root, _, files in os.walk(temp_dir):
          for f in files:
            if f.endswith('.xml'):
              xml_files.append(os.path.join(root, f))

  if not xml_files:
    print('No XML files found in artifacts.')
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