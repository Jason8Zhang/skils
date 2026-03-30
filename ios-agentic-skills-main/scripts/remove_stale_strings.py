#!/usr/bin/env python3
"""
Script to remove STALE strings from Localizable.xcstrings file.
"""

import json
import sys
from pathlib import Path


def remove_stale_strings(file_path: str) -> list[str]:
    """
    Remove strings with extractionState = 'stale' from the xcstrings file.
    Returns list of removed keys.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    strings = data.get('strings', {})
    removed = []
    
    keys_to_remove = []
    for key, value in strings.items():
        extraction_state = value.get('extractionState', '')
        if extraction_state.lower() == 'stale':
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del strings[key]
        removed.append(key)
        print(f"  Removed: '{key}'")
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    return removed


def main():
    if len(sys.argv) < 2:
        print("Usage: python remove_stale_strings.py <path_to_xcstrings>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"Removing stale strings from: {file_path}\n")
    removed = remove_stale_strings(str(file_path))
    print(f"\nDone! Removed {len(removed)} stale strings.")


if __name__ == "__main__":
    main()
