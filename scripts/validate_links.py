#!/usr/bin/env python3
"""
Validate Links Script

Validates character_locations.yml (character ⇄ location links) against schema and vocab.yml.
Includes cardinality validation (e.g., birthplace/current limited to 1 per character).

Usage:
    python scripts/validate_links.py

Exit codes:
    0 - All validations passed
    1 - Validation errors found
"""

import sys
from pathlib import Path
import yaml
import json

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)

# Constants for cardinality values
CARDINALITY_SINGLE = 'single'
CARDINALITY_MULTIPLE = 'multiple'  # Currently used only for documentation; future expansion


def load_yaml(filepath: Path) -> dict:
    """Load a YAML file and return its contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_json(filepath: Path) -> dict:
    """Load a JSON file and return its contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_character_ids(characters_dir: Path) -> set[str]:
    """Get all character IDs from character files."""
    char_ids = set()
    for ext in ['*.yml', '*.yaml']:
        for filepath in characters_dir.glob(ext):
            if filepath.name.startswith('_TEMPLATE'):
                continue
            try:
                data = load_yaml(filepath)
                if data and 'id' in data:
                    char_ids.add(data['id'])
            except Exception:
                pass
    return char_ids


def get_location_ids(locations_dir: Path) -> set[str]:
    """Get all location IDs from location files."""
    loc_ids = set()
    for ext in ['*.yml', '*.yaml']:
        for filepath in locations_dir.glob(ext):
            if filepath.name.startswith('_TEMPLATE'):
                continue
            # Handle both .location.yml and .yml extensions
            try:
                data = load_yaml(filepath)
                if data and 'id' in data:
                    loc_ids.add(data['id'])
            except Exception:
                pass
    return loc_ids


def validate_links(links_path: Path, schema: dict, character_ids: set[str], 
                   location_ids: set[str], vocab: dict) -> tuple[list[str], list[str]]:
    """Validate character_locations.yml. Returns (errors, warnings)."""
    errors = []
    warnings = []
    
    if not links_path.exists():
        print("INFO: No character_locations.yml found")
        return errors, warnings
    
    try:
        data = load_yaml(links_path)
    except Exception as e:
        errors.append(f"character_locations.yml: Failed to load YAML: {e}")
        return errors, warnings
    
    if not data:
        return errors, warnings
    
    # Schema validation
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        errors.append(f"character_locations.yml: Schema validation failed: {e.message}")
        return errors, warnings
    
    valid_kinds = vocab.get('link_kinds', [])
    cardinality = vocab.get('link_cardinality', {})
    links = data.get('links', [])
    
    print(f"Validating {len(links)} links...")
    
    # Track links by character_id and kind for cardinality check
    char_kind_counts = {}
    
    for i, link in enumerate(links):
        char_id = link.get('character_id', '')
        loc_id = link.get('location_id', '')
        kind = link.get('kind', '')
        
        # Character ID validation
        if char_id and char_id not in character_ids:
            errors.append(f"character_locations.yml link[{i}]: character_id '{char_id}' does not exist")
        
        # Location ID validation
        if loc_id and loc_id not in location_ids:
            errors.append(f"character_locations.yml link[{i}]: location_id '{loc_id}' does not exist")
        
        # Kind validation
        if kind and kind not in valid_kinds:
            errors.append(f"character_locations.yml link[{i}]: kind '{kind}' not in vocab.yml link_kinds")
        
        # Track for cardinality check
        if char_id and kind:
            key = (char_id, kind)
            if key not in char_kind_counts:
                char_kind_counts[key] = []
            char_kind_counts[key].append(i)
    
    # Cardinality validation
    for (char_id, kind), indices in char_kind_counts.items():
        if cardinality.get(kind) == CARDINALITY_SINGLE and len(indices) > 1:
            errors.append(
                f"character_locations.yml: character '{char_id}' has {len(indices)} '{kind}' links "
                f"(links [{', '.join(str(i) for i in indices)}]), but only 1 is allowed"
            )
    
    return errors, warnings


def main():
    """Main validation function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    links_path = repo_root / 'links' / 'character_locations.yml'
    characters_dir = repo_root / 'characters'
    locations_dir = repo_root / 'locations'
    schemas_dir = repo_root / 'schemas'
    
    vocab_path = schemas_dir / 'vocab.yml'
    links_schema_path = schemas_dir / 'links.schema.json'
    
    # Load vocab
    if not vocab_path.exists():
        print(f"ERROR: {vocab_path} not found")
        sys.exit(1)
    vocab = load_yaml(vocab_path)
    
    # Load schema
    if not links_schema_path.exists():
        print(f"ERROR: {links_schema_path} not found")
        sys.exit(1)
    links_schema = load_json(links_schema_path)
    
    # Get character and location IDs
    character_ids = get_character_ids(characters_dir)
    location_ids = get_location_ids(locations_dir)
    
    print(f"Found {len(character_ids)} characters and {len(location_ids)} locations")
    
    # Validate links
    print("Validating character_locations.yml...")
    errors, warnings = validate_links(
        links_path, links_schema, character_ids, location_ids, vocab
    )
    
    # Report results
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  ⚠ {warning}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  ✗ {error}")
        print(f"\n✗ Link validation failed with {len(errors)} error(s)")
        sys.exit(1)
    
    print("\n✓ All link validations passed")
    sys.exit(0)


if __name__ == '__main__':
    main()
