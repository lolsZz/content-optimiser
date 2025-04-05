#!/usr/bin/env python3
"""
MDC to MD File Converter

This script converts .mdc files to .md files, creates backups of the originals,
and optionally deletes the original .mdc files after successful conversion.
"""

import os
import shutil
from pathlib import Path
import argparse
import datetime
import sys

def convert_mdc_to_md(directory, backup_dir=None, delete_originals=False, dry_run=False):
    """
    Convert all .mdc files in the specified directory and its subdirectories to .md files.
    
    Args:
        directory (str): The root directory to start the search from
        backup_dir (str): Directory to store backups of original .mdc files
        delete_originals (bool): If True, delete original .mdc files after conversion
        dry_run (bool): If True, only print what would be done without making changes
    
    Returns:
        tuple: (converted_count, backup_count, deleted_count, skipped_count)
    """
    converted_count = 0
    backup_count = 0
    deleted_count = 0
    skipped_count = 0
    
    # Create the backup directory if specified and not in dry run mode
    if backup_dir and not dry_run:
        os.makedirs(backup_dir, exist_ok=True)
        print(f"Backup directory: {backup_dir}")
    
    # Find all .mdc files in the directory and subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mdc"):
                source_path = os.path.join(root, file)
                # Construct the .md file path
                dest_path = os.path.join(root, file[:-4] + ".md")
                
                # Construct the backup file path if backup directory is specified
                backup_path = None
                if backup_dir:
                    # Preserve directory structure in backups
                    rel_path = os.path.relpath(source_path, directory)
                    backup_path = os.path.join(backup_dir, rel_path)
                    backup_dir_path = os.path.dirname(backup_path)
                
                if dry_run:
                    print(f"Would convert: {source_path} -> {dest_path}")
                    if backup_dir:
                        print(f"Would backup: {source_path} -> {backup_path}")
                    if delete_originals:
                        print(f"Would delete original: {source_path}")
                else:
                    try:
                        # Check if the .md file already exists
                        if os.path.exists(dest_path):
                            print(f"Skipping existing: {dest_path}")
                            skipped_count += 1
                            continue
                            
                        # Copy the file with new extension
                        shutil.copy2(source_path, dest_path)
                        print(f"Converted: {source_path} -> {dest_path}")
                        converted_count += 1
                        
                        # Backup the original if backup directory is specified
                        if backup_dir:
                            # Create the directory structure in the backup location
                            os.makedirs(backup_dir_path, exist_ok=True)
                            shutil.copy2(source_path, backup_path)
                            print(f"Backed up: {source_path} -> {backup_path}")
                            backup_count += 1
                        
                        # Delete the original file if requested
                        if delete_originals:
                            os.remove(source_path)
                            print(f"Deleted original: {source_path}")
                            deleted_count += 1
                            
                    except Exception as e:
                        print(f"Error processing {source_path}: {e}", file=sys.stderr)
                        continue
    
    return converted_count, backup_count, deleted_count, skipped_count

def main():
    parser = argparse.ArgumentParser(
        description='Convert .mdc files to .md files with backup and cleanup options')
    parser.add_argument('directory', type=str, help='The directory to search for .mdc files')
    parser.add_argument('--backup-dir', type=str, 
                      help='Directory to store backups of original .mdc files. Defaults to "./mdc_backup_<timestamp>"')
    parser.add_argument('--delete-originals', action='store_true', 
                      help='Delete original .mdc files after successful conversion and backup')
    parser.add_argument('--dry-run', action='store_true', 
                      help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    # Validate the input directory
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory", file=sys.stderr)
        return 1
    
    # Set up the backup directory with timestamp if not specified
    backup_dir = args.backup_dir
    if not backup_dir and not args.dry_run:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"mdc_backup_{timestamp}"
        print(f"Using default backup directory: {backup_dir}")
    
    print(f"{'Dry run: ' if args.dry_run else ''}Converting .mdc files to .md in {args.directory}")
    print(f"{'Would delete' if args.dry_run else 'Will delete'} original .mdc files: {args.delete_originals}")
    
    converted, backed_up, deleted, skipped = convert_mdc_to_md(
        args.directory, 
        backup_dir=backup_dir,
        delete_originals=args.delete_originals,
        dry_run=args.dry_run
    )
    
    print("\nSummary:")
    print(f"Files {'that would be' if args.dry_run else ''} converted: {converted}")
    print(f"Files {'that would be' if args.dry_run else ''} backed up: {backed_up}")
    print(f"Files {'that would be' if args.dry_run else ''} deleted: {deleted}")
    print(f"Files skipped (already exist): {skipped}")
    
    if not args.dry_run and converted > 0:
        print("\nConversion completed successfully!")
    
    return 0

if __name__ == "__main__":
    exit(main())
