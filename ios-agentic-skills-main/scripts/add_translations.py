#!/usr/bin/env python3
"""
Script to add missing translations to Localizable.xcstrings file.
"""

import json
import sys
from pathlib import Path

# Translations to add: key -> {lang: translation}
TRANSLATIONS = {
    "Here is your English text. Have fun coding!": {
        "de": "Hier ist dein englischer Text. Viel Spaß beim Coden!",
        "es": "Aquí está tu texto en inglés. ¡Diviértete programando!",
        "fr": "Voici ton texte en anglais. Amuse-toi bien en codant !",
        "pt-BR": "Aqui está seu texto em inglês. Divirta-se programando!"
    },
}


def add_translations(file_path: str) -> int:
    """
    Add missing translations to the xcstrings file.
    Returns the number of translations added.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    strings = data.get('strings', {})
    count = 0
    
    for key, translations in TRANSLATIONS.items():
        if key not in strings:
            print(f"  Warning: Key not found in file: '{key}'")
            continue
        
        entry = strings[key]
        if 'localizations' not in entry:
            entry['localizations'] = {}
        
        for lang, translation in translations.items():
            if lang not in entry['localizations']:
                entry['localizations'][lang] = {
                    "stringUnit": {
                        "state": "translated",
                        "value": translation
                    }
                }
                count += 1
                print(f"  Added {lang}: '{key}' -> '{translation}'")
            else:
                # Update existing entry if it exists but wasn't translated
                string_unit = entry['localizations'][lang].get('stringUnit', {})
                if string_unit.get('state') != 'translated':
                    entry['localizations'][lang] = {
                        "stringUnit": {
                            "state": "translated", 
                            "value": translation
                        }
                    }
                    count += 1
                    print(f"  Updated {lang}: '{key}' -> '{translation}'")
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    return count


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_translations.py <path_to_xcstrings>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"Adding translations to: {file_path}\n")
    count = add_translations(str(file_path))
    print(f"\nDone! Added {count} translations.")


if __name__ == "__main__":
    main()
