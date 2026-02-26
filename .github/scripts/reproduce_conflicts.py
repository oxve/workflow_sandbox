import os
import subprocess
import shutil
from dataclasses import dataclass
from typing import List

@dataclass
class Scenario:
    name: str
    filename: str
    base_content: str
    main_content: str
    feature_content: str
    description: str

SCENARIOS = [
    Scenario(
        name="simple_one_line",
        filename="simple.txt",
        base_content="line 1\nline 2\nline 3\n",
        main_content="line 1\nline 2 modified by main\nline 3\n",
        feature_content="line 1\nline 2 modified by feature\nline 3\n",
        description="Simple conflict on a single line"
    ),
    Scenario(
        name="adjacent_lines",
        filename="adjacent.txt",
        base_content="line 1\nline 2\nline 3\nline 4\n",
        main_content="line 1\nline 2 modified\nline 3\nline 4\n",
        feature_content="line 1\nline 2\nline 3 modified\nline 4\n",
        description="modifications on adjacent lines"
    ),
    Scenario(
        name="block_replacement",
        filename="block.py",
        base_content="def func():\n    print('hello')\n    print('world')\n    return True\n",
        main_content="def func():\n    # Main rewrote this\n    return 'main'\n",
        feature_content="def func():\n    # Feature rewrote this\n    return 'feature'\n",
        description="Replacing a whole block of code"
    ),
    Scenario(
        name="deletion_vs_modification",
        filename="del_mod.py",
        base_content="def keep_me():\n    pass\n\ndef delete_me_or_mod_me():\n    print('original')\n",
        main_content="def keep_me():\n    pass\n",
        feature_content="def keep_me():\n    pass\n\ndef delete_me_or_mod_me():\n    print('modified')\n",
        description="One side deletes, other modifies"
    ),
    Scenario(
        name="addition_at_end",
        filename="append.txt",
        base_content="start\n",
        main_content="start\nend by main\n",
        feature_content="start\nend by feature\n",
        description="Both add different content at the end"
    ),
    Scenario(
        name="interleaved",
        filename="list.py",
        base_content="items = [\n    'a',\n    'b',\n    'c',\n    'd',\n]\n",
        main_content="items = [\n    'a',\n    'b_mod',\n    'c',\n    'd',\n]\n",
        feature_content="items = [\n    'a',\n    'b',\n    'c_mod',\n    'd',\n]\n",
        description="Interleaved changes in a list"
    ),
    Scenario(
        name="docstring_conflict",
        filename="docs.py",
        base_content='"""\nOriginal docstring.\n"""\ndef func():\n    pass\n',
        main_content='"""\nUpdated docstring by main.\n"""\ndef func():\n    pass\n',
        feature_content='"""\nUpdated docstring by feature.\n"""\ndef func():\n    pass\n',
        description="Conflict in comments/docstrings"
    ),
    Scenario(
        name="import_conflict",
        filename="imports.py",
        base_content="import os\nimport sys\n",
        main_content="import os\nimport sys\nimport json\n",
        feature_content="import os\nimport sys\nimport yaml\n",
        description="Conflict in import statements"
    ),
    Scenario(
        name="variable_rename",
        filename="rename.py",
        base_content="value = 10\nprint(value)\n",
        main_content="count = 10\nprint(count)\n",
        feature_content="total = 10\nprint(total)\n",
        description="Variable renaming conflict"
    ),
    Scenario(
        name="json_conflict",
        filename="config.json",
        base_content='{\n  "version": "1.0",\n  "debug": false\n}\n',
        main_content='{\n  "version": "1.1",\n  "debug": false\n}\n',
        feature_content='{\n  "version": "2.0",\n  "debug": true\n}\n',
        description="Conflict in JSON file"
    ),
    Scenario(
        name="formatting",
        filename="style.js",
        base_content="function test() { return 1; }",
        main_content="function test() {\n    return 1;\n}",
        feature_content="function test() { return 2; }",
        description="Formatting vs Logic change"
    ),
    Scenario(
        name="xml_conflict",
        filename="data.xml",
        base_content="<root>\n  <item>value</item>\n</root>\n",
        main_content="<root>\n  <item attr='1'>value</item>\n</root>\n",
        feature_content="<root>\n  <item>modified</item>\n</root>\n",
        description="Conflict in XML attributes vs content"
    ),
    Scenario(
        name="dependency_lock",
        filename="deps.lock",
        base_content="package-a: 1.0.0\npackage-b: 2.0.0\n",
        main_content="package-a: 1.1.0\npackage-b: 2.0.0\n",
        feature_content="package-a: 1.0.0\npackage-b: 2.1.0\n",
        description="Dependency lock file conflict"
    ),
    Scenario(
        name="readme_header",
        filename="README.md",
        base_content="# Project Title\n\nDescription.\n",
        main_content="# Awesome Project\n\nDescription.\n",
        feature_content="# The Project\n\nDescription.\n",
        description="Markdown header conflict"
    ),
    Scenario(
        name="sql_schema",
        filename="schema.sql",
        base_content="CREATE TABLE users (\n  id INT,\n  name VARCHAR(100)\n);\n",
        main_content="CREATE TABLE users (\n  id INT,\n  name VARCHAR(100),\n  email VARCHAR(100)\n);\n",
        feature_content="CREATE TABLE users (\n  id INT,\n  name VARCHAR(100),\n  age INT\n);\n",
        description="SQL schema conflict"
    ),
    Scenario(
        name="html_structure",
        filename="index.html",
        base_content="<div>\n  <span>Hello</span>\n</div>",
        main_content="<div class='container'>\n  <span>Hello</span>\n</div>",
        feature_content="<div>\n  <p>Hello</p>\n</div>",
        description="HTML structure conflict"
    ),
     Scenario(
        name="css_styles",
        filename="style.css",
        base_content=".btn {\n  color: red;\n  background: white;\n}",
        main_content=".btn {\n  color: blue;\n  background: white;\n}",
        feature_content=".btn {\n  color: red;\n  background: black;\n}",
        description="CSS style conflict"
    ),
    Scenario(
        name="makefile",
        filename="Makefile",
        base_content="build:\n\tgcc main.c\n",
        main_content="build:\n\tgcc -O2 main.c\n",
        feature_content="build:\n\tclang main.c\n",
        description="Makefile command conflict"
    ),
    Scenario(
        name="latex_text",
        filename="paper.tex",
        base_content="\\section{Introduction}\nThis is the intro.\n",
        main_content="\\section{Introduction}\nThis is the robust intro.\n",
        feature_content="\\section{Preliminaries}\nThis is the intro.\n",
        description="Latex text conflict"
    ),
    Scenario(
        name="complex_refactor",
        filename="refactor.py",
        base_content="class A:\n    def method(self):\n        pass\n",
        main_content="class A:\n    def method(self):\n        print('logging')\n",
        feature_content="class B:\n    def method(self):\n        pass\n",
        description="Renaming class vs modifying method"
    )
]

REPO_DIR = "conflict_test_repo"

def setup_repo():
    if os.path.exists(REPO_DIR):
        shutil.rmtree(REPO_DIR)
    os.makedirs(REPO_DIR)
    # Initialize git repo with empty config to avoid using user's global config
    subprocess.run(['git', 'init'], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'config', 'init.defaultBranch', 'main'], cwd=REPO_DIR, check=True)

def create_scenarios():
    setup_repo()

    # Create base state
    print(f"Creating base state with {len(SCENARIOS)} scenarios...")
    for s in SCENARIOS:
        with open(os.path.join(REPO_DIR, s.filename), 'w') as f:
            f.write(s.base_content)

    subprocess.run(['git', 'add', '.'], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=REPO_DIR, check=True)

    # Create feature branch
    subprocess.run(['git', 'checkout', '-b', 'feature'], cwd=REPO_DIR, check=True, capture_output=True)
    for s in SCENARIOS:
        with open(os.path.join(REPO_DIR, s.filename), 'w') as f:
            f.write(s.feature_content)
    subprocess.run(['git', 'commit', '-a', '-m', 'Feature changes'], cwd=REPO_DIR, check=True, capture_output=True)

    # Return to main and apply main changes
    subprocess.run(['git', 'checkout', 'main'], cwd=REPO_DIR, check=True, capture_output=True)
    for s in SCENARIOS:
        with open(os.path.join(REPO_DIR, s.filename), 'w') as f:
            f.write(s.main_content)
    subprocess.run(['git', 'commit', '-a', '-m', 'Main changes'], cwd=REPO_DIR, check=True, capture_output=True)

    # Merge feature into main (expect conflicts)
    print("Merging feature into master...")
    try:
        subprocess.run(['git', 'merge', 'feature'], cwd=REPO_DIR, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Merge failed as expected.")

    # Verify conflicts exist
    result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], cwd=REPO_DIR, capture_output=True, text=True)
    conflicted_files = result.stdout.strip().split('\n')
    print(f"Conflicted files: {len(conflicted_files)}")
    if len(conflicted_files) != len(SCENARIOS):
        print(f"WARNING: Expected {len(SCENARIOS)} conflicts, but got {len(conflicted_files)}.")
        all_files = {s.filename for s in SCENARIOS}
        found_files = set(conflicted_files)
        missing = all_files - found_files
        if missing:
            print(f"Missing conflicts: {missing}")

if __name__ == "__main__":
    create_scenarios()
