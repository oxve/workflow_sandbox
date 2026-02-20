import os
import re
import subprocess
import json
import sys

def resolve_conflict(file_path, gemini_api_key):
    with open(file_path, 'r') as f:
        content = f.read()

    # Regex to find conflict blocks, supporting both standard and diff3 styles
    # Standard: <<<<<<< ours ======= theirs >>>>>>>
    # Diff3: <<<<<<< ours ||||||| base ======= theirs >>>>>>>
    conflict_pattern = re.compile(
        r'<<<<<<<.*?\n(.*?)\n(?:\|\|\|\|\|\|\|.*?\n(.*?)\n)?=======\n(.*?)\n>>>>>>>.*?\n', re.DOTALL
    )

    def replace_conflict(match):
        ours = match.group(1)
        base = match.group(2)
        theirs = match.group(3)

        if base:
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
        else:
            prompt = f"""Resolve this git merge conflict. Provide ONLY the final resolved code with no explanations.
Do not include markdown code blocks (like ```) in your response.

Current changes (HEAD):
{ours}
---
Incoming changes:
{theirs}
"""

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        cmd = [
            'curl', '-s', '-X', 'POST',
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent',
            '-H', 'Content-Type: application/json',
            '-H', 'x-goog-api-key: ${GEMINI_API_KEY}'
            '-d', json.dumps(payload)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            response = json.loads(result.stdout)
            if 'candidates' not in response or not response['candidates']:
                print(f"Warning: No candidates in Gemini response for {file_path}")
                return match.group(0)

            resolved_text = response['candidates'][0]['content']['parts'][0]['text'].strip()
            # Remove any accidentally included markdown markers
            resolved_text = re.sub(r'^```.*?\n', '', resolved_text)
            resolved_text = re.sub(r'\n```$', '', resolved_text)
            return resolved_text + '\n'
        except Exception as e:
            print(f"Error resolving conflict in {file_path}: {e}")
            return match.group(0) # Keep the conflict if it fails

    new_content = conflict_pattern.sub(replace_conflict, content)

    with open(file_path, 'w') as f:
        f.write(new_content)

def main():
    gemini_api_key = os.environ.get('GEMINI_SECRET')
    if not gemini_api_key:
        print("GEMINI_SECRET environment variable not set.")
        sys.exit(1)

    # Get conflicting files
    result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True)
    conflicting_files = result.stdout.strip().split('\n')

    if not conflicting_files or conflicting_files == ['']:
        print("No conflicting files found.")
        return

    for file_path in conflicting_files:
        if os.path.exists(file_path):
            print(f"Resolving conflicts in {file_path}...")
            resolve_conflict(file_path, gemini_api_key)
            # Check if all conflicts were resolved
            with open(file_path, 'r') as f:
                if '<<<<<<<' not in f.read():
                    subprocess.run(['git', 'add', file_path])
                    print(f"Successfully resolved conflicts in {file_path}")
                else:
                    print(f"Failed to resolve all conflicts in {file_path}")

if __name__ == "__main__":
    main()
