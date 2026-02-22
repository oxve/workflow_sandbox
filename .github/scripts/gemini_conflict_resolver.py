import os
import re
import subprocess
import json
import sys
import requests


def resolve_conflict(file_path, gemini_api_key):
  with open(file_path, 'r') as f:
    content = f.read()

  # Regex to find conflict blocks, supporting both standard and diff3 styles
  # Standard: <<<<<<< ours ======= theirs >>>>>>>
  # Diff3: <<<<<<< ours ||||||| base ======= theirs >>>>>>>
  # Uses MULTILINE to match start of lines and DOTALL to match content across lines.
  # Handles optional indentation before markers.
  conflict_pattern = re.compile(
      r'^[ \t]*<<<<<<<.*?\n(.*?)(?:^[ \t]*\|\|\|\|\|\|\|.*?\n(.*?))?^[ \t]*=======\n(.*?)^[ \t]*>>>>>>>.*?(?:\n|$)',
      re.DOTALL | re.MULTILINE)

  def replace_conflict(match):
    ours = match.group(1)
    base = match.group(2)
    theirs = match.group(3)

    prompt = f"""Resolve this git merge conflict. Provide ONLY the final resolved code with no explanations.
Do not include markdown code blocks (like ```) in your response.

Current changes (HEAD):
{ours}
---
Common ancestor:
{base}
---
Incoming changes:
{theirs}
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={gemini_api_key}'
    headers = {'Content-Type': 'application/json'}

    try:
      response = requests.post(url, headers=headers, json=payload)
      response.raise_for_status()
      response_data = response.json()
      if 'candidates' not in response_data or not response_data['candidates']:
        return match.group(0)

      resolved_text = response_data['candidates'][0]['content']['parts'][0][
          'text'].strip()
      # Remove any accidentally included markdown markers
      resolved_text = re.sub(r'^```.*?\n', '', resolved_text)
      resolved_text = re.sub(r'\n```$', '', resolved_text)
      return resolved_text + '\n'
    except requests.exceptions.RequestException as e:
      print(f"Error resolving conflict in {file_path}: {e}")
      return match.group(0)  # Keep the conflict if it fails

  new_content = conflict_pattern.sub(replace_conflict, content)

  with open(file_path, 'w') as f:
    f.write(new_content)


def main():
  gemini_api_key = os.environ.get('GEMINI_API_KEY')
  if not gemini_api_key:
    print("GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

  conflicting_files = sys.argv[1:]

  if not conflicting_files:
    print("Usage: python3 gemini_resolve_conflicts.py <file1> <file2> ...")
    sys.exit(1)

  for file_path in conflicting_files:
    if os.path.exists(file_path):
      print(f"Resolving conflicts in {file_path}...")
      resolve_conflict(file_path, gemini_api_key)


if __name__ == "__main__":
  main()
