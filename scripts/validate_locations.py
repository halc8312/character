#!/usr/bin/env python3
"""
Validate Locations Script

Validates location, map, and link YAML files against their schemas and vocab.yml.

Usage:
    python scripts/validate_locations.py

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


def load_yaml(filepath: Path) -> dict:
    """Load a YAML file and return its contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_json(filepath: Path) -> dict:
    """Load a JSON file and return its contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_location_files(locations_dir: Path) -> list[Path]:
    """Get all location YAML files, excluding the template."""
    files = []
    for pattern in ['*.location.yml', '*.location.yaml']:
        files.extend(locations_dir.glob(pattern))
    return [f for f in files if not f.name.startswith('_TEMPLATE')]


def get_map_files(maps_dir: Path) -> list[Path]:
    """Get all map YAML files, excluding the template."""
    files = []
    for pattern in ['*.map.yml', '*.map.yaml']:
        files.extend(maps_dir.glob(pattern))
    return [f for f in files if not f.name.startswith('_TEMPLATE')]


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


def validate_locations(locations_dir: Path, schema: dict, vocab: dict) -> tuple[list[str], list[str]]:
    """Validate all location files. Returns (errors, warnings)."""
    errors = []
    warnings = []
    
    location_files = get_location_files(locations_dir)
    location_ids = set()
    locations_data = {}
    
    valid_types = vocab.get('location_types', [])
    valid_prefixes = vocab.get('tag_prefixes', [])
    
    for filepath in sorted(location_files):
        filename = filepath.stem.replace('.location', '')
        
        try:
            data = load_yaml(filepath)
        except Exception as e:
            errors.append(f"{filepath.name}: Failed to load YAML: {e}")
            continue
        
        if not data:
            errors.append(f"{filepath.name}: Empty file")
            continue
        
        # Schema validation
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            errors.append(f"{filepath.name}: Schema validation failed: {e.message}")
            continue
        
        loc_id = data.get('id', '')
        location_ids.add(loc_id)
        locations_data[loc_id] = data
        
        # ID/filename match
        if loc_id != filename:
            errors.append(f"{filepath.name}: ID '{loc_id}' does not match filename '{filename}'")
        
        # Type validation
        loc_type = data.get('profile', {}).get('type', '')
        if loc_type and loc_type not in valid_types:
            errors.append(f"{filepath.name}: type '{loc_type}' not in vocab.yml location_types")
        
        # Tag prefix validation
        tags = data.get('tags', [])
        for tag in tags:
            if '/' not in tag:
                warnings.append(f"{filepath.name}: tag '{tag}' not in prefix/value format")
                continue
            prefix = tag.split('/')[0]
            if prefix not in valid_prefixes:
                warnings.append(f"{filepath.name}: tag prefix '{prefix}' not in vocab.yml tag_prefixes")
    
    # Second pass: validate parent_id references
    for loc_id, data in locations_data.items():
        parent_id = data.get('profile', {}).get('parent_id')
        if parent_id and parent_id not in location_ids:
            errors.append(f"Location '{loc_id}': parent_id '{parent_id}' does not exist")
    
    # Third pass: check for circular references in parent_id chain
    def has_cycle(start_id, visited):
        """Check if following parent_id chain from start_id creates a cycle."""
        if start_id in visited:
            return True
        visited.add(start_id)
        data = locations_data.get(start_id)
        if not data:
            return False
        parent_id = data.get('profile', {}).get('parent_id')
        if not parent_id:
            return False
        return has_cycle(parent_id, visited)
    
    for loc_id in locations_data:
        if has_cycle(loc_id, set()):
            errors.append(f"Location '{loc_id}': circular reference detected in parent_id chain")
    
    return errors, warnings


def validate_maps(maps_dir: Path, schema: dict, location_ids: set[str], vocab: dict) -> tuple[list[str], list[str]]:
    """Validate all map files. Returns (errors, warnings)."""
    errors = []
    warnings = []
    
    map_files = get_map_files(maps_dir)
    valid_types = vocab.get('location_types', [])
    
    for filepath in sorted(map_files):
        filename = filepath.stem.replace('.map', '')
        
        try:
            data = load_yaml(filepath)
        except Exception as e:
            errors.append(f"{filepath.name}: Failed to load YAML: {e}")
            continue
        
        if not data:
            errors.append(f"{filepath.name}: Empty file")
            continue
        
        # Schema validation
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            errors.append(f"{filepath.name}: Schema validation failed: {e.message}")
            continue
        
        map_id = data.get('id', '')
        
        # ID/filename match
        if map_id != filename:
            errors.append(f"{filepath.name}: ID '{map_id}' does not match filename '{filename}'")
        
        # root_location_id validation
        root_id = data.get('root_location_id', '')
        if root_id and root_id not in location_ids:
            errors.append(f"{filepath.name}: root_location_id '{root_id}' does not exist")
        
        # include.types validation
        include_types = data.get('include', {}).get('types', [])
        for t in include_types:
            if t not in valid_types:
                warnings.append(f"{filepath.name}: include.types '{t}' not in vocab.yml location_types")
    
    return errors, warnings


def validate_links(links_path: Path, schema: dict, character_ids: set[str], location_ids: set[str], vocab: dict) -> tuple[list[str], list[str]]:
    """Validate character_locations.yml. Returns (errors, warnings)."""
    errors = []
    warnings = []
    
    if not links_path.exists():
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
    links = data.get('links', [])
    
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
    
    return errors, warnings


def main():
    """Main validation function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    locations_dir = repo_root / 'locations'
    maps_dir = repo_root / 'maps'
    links_path = repo_root / 'links' / 'character_locations.yml'
    characters_dir = repo_root / 'characters'
    schemas_dir = repo_root / 'schemas'
    
    vocab_path = schemas_dir / 'vocab.yml'
    location_schema_path = schemas_dir / 'location.schema.json'
    map_schema_path = schemas_dir / 'map.schema.json'
    links_schema_path = schemas_dir / 'links.schema.json'
    
    all_errors = []
    all_warnings = []
    
    # Load vocab
    if not vocab_path.exists():
        print("ERROR: schemas/vocab.yml not found")
        sys.exit(1)
    
    try:
        vocab = load_yaml(vocab_path)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in vocab.yml: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"ERROR: Failed to read vocab.yml: {e}")
        sys.exit(1)
    
    # Load schemas
    schemas = {}
    for name, path in [('location', location_schema_path), ('map', map_schema_path), ('links', links_schema_path)]:
        if path.exists():
            try:
                schemas[name] = load_json(path)
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON in {path.name}: {e}")
                sys.exit(1)
            except IOError as e:
                print(f"ERROR: Failed to read {path.name}: {e}")
                sys.exit(1)
        else:
            print(f"WARNING: {path.name} not found, skipping {name} validation")
    
    # Get character IDs for link validation
    character_ids = get_character_ids(characters_dir) if characters_dir.exists() else set()
    
    # Validate locations
    location_ids = set()
    if locations_dir.exists() and 'location' in schemas:
        location_files = get_location_files(locations_dir)
        if location_files:
            print(f"Validating {len(location_files)} location(s)...")
            errors, warnings = validate_locations(locations_dir, schemas['location'], vocab)
            all_errors.extend(errors)
            all_warnings.extend(warnings)
            
            # Collect valid location IDs for map validation
            for f in location_files:
                try:
                    data = load_yaml(f)
                    if data and 'id' in data:
                        location_ids.add(data['id'])
                except Exception:
                    pass
        else:
            print("INFO: No location files found (excluding template)")
    
    # Validate maps
    if maps_dir.exists() and 'map' in schemas:
        map_files = get_map_files(maps_dir)
        if map_files:
            print(f"Validating {len(map_files)} map(s)...")
            errors, warnings = validate_maps(maps_dir, schemas['map'], location_ids, vocab)
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        else:
            print("INFO: No map files found (excluding template)")
    
    # Validate links
    if links_path.exists() and 'links' in schemas:
        print("Validating character_locations.yml...")
        errors, warnings = validate_links(links_path, schemas['links'], character_ids, location_ids, vocab)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    
    # Output results
    for warning in all_warnings:
        print(f"WARNING: {warning}")
    
    for error in all_errors:
        print(f"ERROR: {error}")
    
    if all_errors:
        print(f"\n✗ Validation failed with {len(all_errors)} error(s)")
        sys.exit(1)
    else:
        print(f"\n✓ All location validations passed")
        if all_warnings:
            print(f"  ({len(all_warnings)} warning(s))")
        sys.exit(0)


if __name__ == '__main__':
    main()
