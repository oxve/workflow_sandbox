#!/usr/bin/env python3
import os
import argparse
import random
import uuid

def generate_python_snippet(size_lines, snippet_type, cid):
    """Generates a random but valid-ish Python snippet."""
    lines = []
    
    # We can use simple things like assignments, prints, simple functions
    for i in range(size_lines):
        choice = random.choice(['assign', 'print', 'pass'])
        if choice == 'assign':
            lines.append(f"    var_{snippet_type}_{cid}_{i} = {random.randint(1, 1000)}")
        elif choice == 'print':
            lines.append(f"    print('This is {snippet_type} line {i}')")
        else:
            lines.append(f"    # {snippet_type} comment {i}")
            
    return "\n".join(lines) + "\n"

def generate_conflict_block(conflict_size, with_base=True):
    cid = str(uuid.uuid4())[:8]
    
    ours_code = generate_python_snippet(conflict_size, 'ours', cid)
    base_code = generate_python_snippet(conflict_size, 'base', cid) if with_base else ""
    theirs_code = generate_python_snippet(conflict_size, 'theirs', cid)
    
    block = f"<<<<<<< HEAD\n{ours_code}"
    if with_base:
        block += f"||||||| parent of {cid}\n{base_code}"
    block += f"=======\n{theirs_code}>>>>>>> {cid}\n"
    
    return block

def generate_file_with_conflicts(output_path, num_conflicts, max_conflict_size, use_diff3=True):
    content = ["def generated_function_runner():\n"]
    content.append("    print('Starting execution')\n\n")
    
    for i in range(num_conflicts):
        size = random.randint(1, max_conflict_size)
        conflict_block = generate_conflict_block(size, with_base=use_diff3)
        content.append(conflict_block)
        content.append("\n    print('Intermediate step')\n\n")
        
    content.append("    print('Finished execution')\n")
    
    with open(output_path, 'w') as f:
        f.write("".join(content))

def main():
    parser = argparse.ArgumentParser(description="Generate files with git conflicts")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to save generated files")
    parser.add_argument("--num-files", type=int, default=5, help="Number of files to generate")
    parser.add_argument("--conflicts-per-file", type=int, default=3, help="Max conflicts per file")
    parser.add_argument("--max-size", type=int, default=5, help="Max random lines per conflict block")
    parser.add_argument("--no-diff3", action="store_true", help="Do not include base (|||||||) block")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Generating {args.num_files} files in {args.output_dir}...")
    for i in range(args.num_files):
        filename = f"conflict_test_{i}.py"
        filepath = os.path.join(args.output_dir, filename)
        num_conflicts = random.randint(1, args.conflicts_per_file)
        generate_file_with_conflicts(filepath, num_conflicts, args.max_size, use_diff3=not args.no_diff3)
        print(f"Generated {filepath} with {num_conflicts} conflicts.")
        
    print("Done generating files.")

if __name__ == "__main__":
    main()
