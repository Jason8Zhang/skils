#!/usr/bin/env python3
"""
Script to extract STALE and NEW strings from a Localizable.xcstrings file.
Also finds strings that are missing translations for non-English languages.
Outputs lists for verification and translation updates.
"""

import json
import sys
import argparse
from pathlib import Path

# Default languages to check if none are provided via arguments
DEFAULT_LANGUAGES = {'de', 'es', 'fr', 'pt-BR'}

def analyze_xcstrings(file_path: str, target_languages: set) -> tuple[dict, dict, dict]:
    """
    Analyze an xcstrings file and extract strings with STALE or NEW states,
    as well as strings missing translations in non-English languages.
    
    Returns:
        Tuple of (stale_strings, new_strings, missing_translations)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stale_strings = {}
    new_strings = {}
    missing_translations = {}
    
    strings = data.get('strings', {})
    source_language = data.get('sourceLanguage', 'en')
    
    for key, value in strings.items():
        comment = value.get('comment', '')
        localizations = value.get('localizations', {})
        
        # Check extractionState at the top level (this is where STALE lives!)
        extraction_state = value.get('extractionState', '')
        
        if extraction_state.lower() == 'stale':
            # Get the English/source value for context
            source_value = key
            if source_language in localizations:
                source_value = localizations[source_language].get('stringUnit', {}).get('value', key)
            elif 'en' in localizations:
                source_value = localizations['en'].get('stringUnit', {}).get('value', key)
            
            stale_strings[key] = {
                'comment': comment,
                'source_value': source_value
            }
            continue  # Skip further analysis for stale strings
        
        # Track NEW strings and missing translations
        new_langs = {}
        missing_langs = []
        
        for lang, lang_data in localizations.items():
            string_unit = lang_data.get('stringUnit', {})
            state = string_unit.get('state', '')
            translation_value = string_unit.get('value', '')
            
            if state.lower() == 'new':
                new_langs[lang] = translation_value
        
        # Check for missing translations in expected languages
        for lang in target_languages:
            if lang not in localizations:
                missing_langs.append(lang)
        
        if new_langs:
            # Get source value for context
            source_value = key
            if 'en' in localizations:
                source_value = localizations['en'].get('stringUnit', {}).get('value', key)
            new_strings[key] = {
                'comment': comment,
                'languages': new_langs,
                'source_value': source_value
            }
        
        if missing_langs and extraction_state.lower() != 'stale':
            # Get the English source value for context
            en_value = key
            if 'en' in localizations:
                en_value = localizations['en'].get('stringUnit', {}).get('value', key)
            elif source_language in localizations:
                en_value = localizations[source_language].get('stringUnit', {}).get('value', key)
            
            missing_translations[key] = {
                'comment': comment,
                'missing_languages': missing_langs,
                'source_value': en_value
            }
    
    return stale_strings, new_strings, missing_translations


def print_results(stale: dict, new: dict, missing: dict, target_languages: set) -> None:
    """Print the results in a readable format."""
    print("=" * 80)
    print("LOCALIZATION STATUS REPORT")
    print(f"Checking for languages: {', '.join(sorted(target_languages))}")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print(f"STALE STRINGS ({len(stale)} total)")
    print("These strings may no longer be needed in the codebase.")
    print("=" * 80)
    
    if stale:
        for i, (key, info) in enumerate(sorted(stale.items()), 1):
            print(f"\n{i}. \"{key}\"")
            if info['comment']:
                print(f"   Comment: {info['comment']}")
    else:
        print("\n   No stale strings found.")
    
    print("\n" + "=" * 80)
    print(f"NEW STRINGS / MISSING TRANSLATIONS ({len(missing)} total)")
    print("These strings need translations added for non-English languages.")
    print("=" * 80)
    
    if missing:
        for i, (key, info) in enumerate(sorted(missing.items()), 1):
            print(f"\n{i}. \"{key}\"")
            if info['comment']:
                print(f"   Comment: {info['comment']}")
            print(f"   Missing: {', '.join(sorted(info['missing_languages']))}")
    else:
        print(f"\n   All strings have translations for {', '.join(sorted(target_languages))}.")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total STALE strings: {len(stale)}")
    print(f"Total strings needing translations: {len(missing)}")


def main():
    parser = argparse.ArgumentParser(description="Analyze Localizable.xcstrings for stale strings and missing translations.")
    
    parser.add_argument(
        "file_path", 
        nargs="?",
        default=str(Path(__file__).parent.parent / "YourApp" / "Localizable.xcstrings"),
        help="Path to the Localizable.xcstrings file"
    )
    
    parser.add_argument(
        "--languages", 
        type=str, 
        help=f"Comma-separated list of language codes to check (default: {', '.join(sorted(DEFAULT_LANGUAGES))})"
    )
    
    args = parser.parse_args()
    
    file_path = Path(args.file_path)
    
    if args.languages:
        target_languages = set(lang.strip() for lang in args.languages.split(','))
    else:
        target_languages = DEFAULT_LANGUAGES
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        print(f"Usage: {sys.argv[0]} [path/to/Localizable.xcstrings] [--languages de,es,fr]")
        sys.exit(1)
    
    print(f"Analyzing: {file_path}\n")
    
    stale, new, missing = analyze_xcstrings(str(file_path), target_languages)
    print_results(stale, new, missing, target_languages)


if __name__ == "__main__":
    main()
