#!/usr/bin/env python3
"""
Character YAML Validation Script

Validates all character files in the characters/ directory against:
1. JSON Schema (character.schema.json)
2. Filename/ID consistency
3. Relationship target existence
4. Relationship type validity (vocab.yml)
5. Tag prefix validity (vocab.yml)
6. Date format validity

Usage:
    python scripts/validate_characters.py

Exit codes:
    0 - All validations passed
    1 - One or more validations failed
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path

import yaml
import json
from jsonschema import validate, ValidationError, Draft7Validator


def load_yaml(filepath: Path) -> dict:
    """Load a YAML file and return its contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_json(filepath: Path) -> dict:
    """Load a JSON file and return its contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_character_files(characters_dir: Path) -> list[Path]:
    """Get all character YAML files, excluding the template."""
    files = []
    for ext in ['*.yml', '*.yaml']:
        files.extend(characters_dir.glob(ext))
    # Exclude template file
    return [f for f in files if not f.name.startswith('_TEMPLATE')]


def validate_schema(character: dict, schema: dict, filepath: Path) -> list[str]:
    """Validate character against JSON schema."""
    errors = []
    try:
        validate(instance=character, schema=schema)
    except ValidationError as e:
        errors.append(f"Schema validation failed: {e.message}")
        # Get all errors for better reporting
        validator = Draft7Validator(schema)
        for error in validator.iter_errors(character):
            if error.message != e.message:
                path = " -> ".join(str(p) for p in error.absolute_path)
                if path:
                    errors.append(f"  - {path}: {error.message}")
                else:
                    errors.append(f"  - {error.message}")
    return errors


def validate_id_filename(character: dict, filepath: Path) -> list[str]:
    """Check that the character ID matches the filename."""
    errors = []
    expected_id = filepath.stem  # filename without extension
    actual_id = character.get('id', '')
    
    if actual_id != expected_id:
        errors.append(
            f"ID mismatch: file is '{filepath.name}' but id is '{actual_id}' "
            f"(expected id: '{expected_id}')"
        )
    return errors


def validate_relationships(
    character: dict, 
    valid_ids: set[str], 
    valid_types: list[str],
    filepath: Path
) -> list[str]:
    """Validate relationship targets and types."""
    errors = []
    relationships = character.get('relationships', [])
    
    for i, rel in enumerate(relationships):
        target_id = rel.get('target_id', '')
        rel_type = rel.get('type', '')
        
        # Check target exists
        if target_id and target_id not in valid_ids:
            errors.append(
                f"relationships[{i}].target_id '{target_id}' does not exist "
                f"in characters/ directory"
            )
        
        # Check type is valid
        if rel_type and rel_type not in valid_types:
            errors.append(
                f"relationships[{i}].type '{rel_type}' is not in vocab.yml "
                f"relationship_types"
            )
    
    return errors


def validate_tags(character: dict, valid_prefixes: list[str], filepath: Path) -> list[str]:
    """Validate tag prefixes against vocab.yml."""
    errors = []
    tags = character.get('tags', [])
    
    for tag in tags:
        if '/' not in tag:
            errors.append(f"Tag '{tag}' is not in prefix/value format")
            continue
        
        prefix = tag.split('/')[0]
        if prefix not in valid_prefixes:
            errors.append(
                f"Tag prefix '{prefix}' in tag '{tag}' is not in vocab.yml "
                f"tag_prefixes (valid: {', '.join(valid_prefixes)})"
            )
    
    return errors


def validate_dates(character: dict, filepath: Path) -> list[str]:
    """Validate date formats in meta section."""
    errors = []
    meta = character.get('meta', {})
    
    date_fields = ['created', 'updated']
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    for field in date_fields:
        value = meta.get(field, '')
        if not value:
            continue
            
        if not date_pattern.match(value):
            errors.append(
                f"meta.{field} '{value}' is not in YYYY-MM-DD format"
            )
        else:
            # Try to parse as actual date
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                errors.append(
                    f"meta.{field} '{value}' is not a valid date"
                )
    
    return errors


def validate_graph(graph_path: Path, valid_ids: set[str], valid_types: list[str]) -> list[str]:
    """Validate the relations/graph.yml file if it exists."""
    errors = []
    
    if not graph_path.exists():
        return errors
    
    try:
        graph = load_yaml(graph_path)
    except Exception as e:
        errors.append(f"Failed to load graph.yml: {e}")
        return errors
    
    if graph is None:
        return errors
    
    edges = graph.get('edges', [])
    if not edges:
        return errors
    
    for i, edge in enumerate(edges):
        a = edge.get('a', '')
        b = edge.get('b', '')
        rel_type = edge.get('type', '')
        
        if a and a not in valid_ids:
            errors.append(f"graph.yml edges[{i}].a '{a}' does not exist in characters/")
        if b and b not in valid_ids:
            errors.append(f"graph.yml edges[{i}].b '{b}' does not exist in characters/")
        if rel_type and rel_type not in valid_types:
            errors.append(
                f"graph.yml edges[{i}].type '{rel_type}' is not in vocab.yml relationship_types"
            )
    
    return errors


def main():
    """Main validation function."""
    # Determine paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    characters_dir = repo_root / 'characters'
    schema_path = repo_root / 'schemas' / 'character.schema.json'
    vocab_path = repo_root / 'schemas' / 'vocab.yml'
    graph_path = repo_root / 'relations' / 'graph.yml'
    
    # Check required files exist
    if not characters_dir.exists():
        print("ERROR: characters/ directory not found")
        sys.exit(1)
    
    if not schema_path.exists():
        print("ERROR: schemas/character.schema.json not found")
        sys.exit(1)
    
    if not vocab_path.exists():
        print("ERROR: schemas/vocab.yml not found")
        sys.exit(1)
    
    # Load schema and vocab
    try:
        schema = load_json(schema_path)
    except Exception as e:
        print(f"ERROR: Failed to load schema: {e}")
        sys.exit(1)
    
    try:
        vocab = load_yaml(vocab_path)
    except Exception as e:
        print(f"ERROR: Failed to load vocab.yml: {e}")
        sys.exit(1)
    
    valid_types = vocab.get('relationship_types', [])
    valid_prefixes = vocab.get('tag_prefixes', [])
    
    # Get character files
    character_files = get_character_files(characters_dir)
    
    if not character_files:
        print("INFO: No character files found (excluding template)")
        print("✓ Validation complete: 0 files checked")
        sys.exit(0)
    
    # Build set of valid character IDs
    valid_ids = {f.stem for f in character_files}
    
    # Validate each character
    all_errors: dict[str, list[str]] = {}
    files_checked = 0
    
    for filepath in sorted(character_files):
        file_errors = []
        files_checked += 1
        
        # Load character
        try:
            character = load_yaml(filepath)
        except Exception as e:
            file_errors.append(f"Failed to parse YAML: {e}")
            all_errors[str(filepath)] = file_errors
            continue
        
        if character is None:
            file_errors.append("File is empty or invalid YAML")
            all_errors[str(filepath)] = file_errors
            continue
        
        # Run validations
        file_errors.extend(validate_schema(character, schema, filepath))
        file_errors.extend(validate_id_filename(character, filepath))
        file_errors.extend(validate_relationships(character, valid_ids, valid_types, filepath))
        file_errors.extend(validate_tags(character, valid_prefixes, filepath))
        file_errors.extend(validate_dates(character, filepath))
        
        if file_errors:
            all_errors[str(filepath)] = file_errors
    
    # Validate graph.yml
    graph_errors = validate_graph(graph_path, valid_ids, valid_types)
    if graph_errors:
        all_errors['relations/graph.yml'] = graph_errors
    
    # Output results
    print("=" * 60)
    print("Character Validation Report")
    print("=" * 60)
    
    if all_errors:
        print(f"\n❌ Validation FAILED\n")
        print(f"Files checked: {files_checked}")
        print(f"Files with errors: {len([k for k in all_errors if 'graph.yml' not in k])}")
        print()
        
        for filepath, errors in all_errors.items():
            print(f"\n📄 {filepath}")
            for error in errors:
                print(f"   ⚠ {error}")
        
        print("\n" + "=" * 60)
        sys.exit(1)
    else:
        print(f"\n✓ All validations passed!\n")
        print(f"Files checked: {files_checked}")
        print(f"Schema: character.schema.json")
        print(f"Vocabulary: vocab.yml")
        print("\n" + "=" * 60)
        sys.exit(0)


if __name__ == '__main__':
    main()
