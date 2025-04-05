#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import argparse

def convert_mdc_to_md(directory, dry_run=False):
    """
    Convert all .mdc files in the specified directory and its subdirectories to .md files.
    
    Args:
        directory (str): The root directory to start the search from
        dry_run (bool): If True, only print what would be done without making changes
    
    Returns:
        int: The number of files converted
    """
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mdc"):
                source_path = os.path.join(root, file)
                dest_path = os.path.join(root, file[:-4] + ".md")
                
                if dry_run:
                    print(f"Would convert: {source_path} -> {dest_path}")
                else:
                    try:
                        # Copy the file with new extension
                        shutil.copy2(source_path, dest_path)
                        print(f"Converted: {source_path} -> {dest_path}")
                        
                        # Optionally remove the original file
                        # os.remove(source_path)
                        # print(f"Removed original: {source_path}")
                    except Exception as e:
                        print(f"Error converting {source_path}: {e}")
                        continue
                
                count += 1
    
    return count

def main():
    parser = argparse.ArgumentParser(description='Convert .mdc files to .md files')
    parser.add_argument('directory', type=str, help='The directory to search for .mdc files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--remove-originals', action='store_true', help='Remove original .mdc files after conversion')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        return 1
    
    print(f"{'Dry run: ' if args.dry_run else ''}Converting .mdc files to .md in {args.directory} and its subdirectories...")
    count = convert_mdc_to_md(args.directory, args.dry_run)
    
    if args.remove_originals and not args.dry_run:
        print("Removing original .mdc files...")
        for root, _, files in os.walk(args.directory):
            for file in files:
                if file.endswith(".mdc"):
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(root, file[:-4] + ".md")
                    
                    # Only remove if the .md file exists
                    if os.path.exists(dest_path):
                        os.remove(source_path)
                        print(f"Removed original: {source_path}")
    
    print(f"Conversion {'would have been' if args.dry_run else 'was'} performed on {count} files.")
    return 0

if __name__ == "__main__":
    exit(main())
