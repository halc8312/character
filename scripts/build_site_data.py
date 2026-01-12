#!/usr/bin/env python3
"""
Build Site Data Script

Generates JSON files for the GitHub Pages site from character YAML files.

Outputs:
  - site/data/characters.json: Character list for index/detail views
  - site/data/graph.json: Nodes and edges for graph visualization
  - site/data/layout.json: Empty object if not exists (for layout persistence)

Usage:
    python scripts/build_site_data.py

Exit codes:
    0 - Build successful
    1 - Build failed (invalid data or missing references)
"""

import sys
import json
from pathlib import Path
import yaml


def load_yaml(filepath: Path) -> dict:
    """Load a YAML file and return its contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_character_files(characters_dir: Path) -> list[Path]:
    """Get all character YAML files, excluding the template."""
    files = []
    for ext in ['*.yml', '*.yaml']:
        files.extend(characters_dir.glob(ext))
    return [f for f in files if not f.name.startswith('_TEMPLATE')]


def extract_character_data(character: dict) -> dict:
    """Extract relevant fields from a character YAML for the characters.json."""
    profile = character.get('profile', {})
    name_val = profile.get('name', '')
    
    # Handle name: can be string or dict with display/romanized
    if isinstance(name_val, dict):
        name_display = name_val.get('display', name_val.get('full', ''))
        name_romanized = name_val.get('romanized', '')
    else:
        name_display = name_val
        name_romanized = ''
    
    ai_portrayal = character.get('ai_portrayal', {})
    story = character.get('story', {})
    
    # Build summary from guidelines if no explicit summary
    ai_summary = ''
    if isinstance(ai_portrayal, dict):
        guidelines = ai_portrayal.get('guidelines', [])
        if guidelines:
            ai_summary = guidelines[0] if isinstance(guidelines, list) else str(guidelines)
    
    result = {
        'id': character.get('id', ''),
        'name_display': name_display,
        'name_romanized': name_romanized,
        'aliases': profile.get('aliases', []),
        'tags': character.get('tags', []),
        'role_in_story': story.get('role_in_narrative', ''),
        'ai_summary': ai_summary,
    }
    
    # Optional fields
    age = profile.get('age')
    if age is not None:
        result['age'] = age
    
    species_tags = [t for t in character.get('tags', []) if t.startswith('species/')]
    if species_tags:
        result['species'] = species_tags[0].split('/')[1]
    
    role = profile.get('role')
    if role:
        result['occupation'] = role
    
    affiliation = profile.get('affiliation')
    if affiliation:
        result['affiliation_primary'] = affiliation
    
    # Add personality summary
    personality = character.get('personality', {})
    if isinstance(personality, dict):
        result['personality_summary'] = personality.get('summary', '')
    
    return result


def build_edges_from_characters(characters: list[dict], valid_ids: set[str]) -> list[dict]:
    """Build edges from character relationships arrays."""
    edges = []
    seen_edges = set()
    
    for char in characters:
        source_id = char.get('id', '')
        relationships = char.get('relationships', [])
        
        for rel in relationships:
            target_id = rel.get('target_id', '')
            rel_type = rel.get('type', 'unknown')
            
            if not target_id or target_id not in valid_ids:
                continue
            
            # Normalize edge (alphabetical order for stable_id)
            if source_id < target_id:
                norm_source, norm_target = source_id, target_id
            else:
                norm_source, norm_target = target_id, source_id
            
            stable_id = f"{norm_source}__{rel_type}__{norm_target}"
            
            if stable_id in seen_edges:
                continue
            
            seen_edges.add(stable_id)
            
            edge = {
                'id': stable_id,
                'source': source_id,
                'target': target_id,
                'type': rel_type,
                'intensity': rel.get('intensity', 3),
                'summary': rel.get('description', ''),
                'tags': []
            }
            
            # Add dynamic tags if mutual
            if rel.get('mutual'):
                edge['tags'].append('dynamic/mutual')
            
            edges.append(edge)
    
    return edges


def build_edges_from_graph_yml(graph_path: Path, valid_ids: set[str], valid_types: list[str]) -> list[dict]:
    """Build edges from relations/graph.yml if it exists."""
    if not graph_path.exists():
        return []
    
    graph = load_yaml(graph_path)
    if graph is None:
        return []
    
    edges_data = graph.get('edges', [])
    if not edges_data:
        return []
    
    edges = []
    for edge in edges_data:
        source = edge.get('a', '')
        target = edge.get('b', '')
        rel_type = edge.get('type', 'unknown')
        
        if not source or not target:
            continue
        
        # Normalize for stable_id
        if source < target:
            norm_source, norm_target = source, target
        else:
            norm_source, norm_target = target, source
        
        stable_id = f"{norm_source}__{rel_type}__{norm_target}"
        
        edges.append({
            'id': stable_id,
            'source': source,
            'target': target,
            'type': rel_type,
            'intensity': edge.get('intensity', 3),
            'summary': edge.get('summary', ''),
            'tags': edge.get('tags', [])
        })
    
    return edges


def merge_edges(char_edges: list[dict], graph_edges: list[dict]) -> list[dict]:
    """Merge edges from characters and graph.yml. graph.yml takes precedence."""
    edge_map = {}
    
    # Add character edges first
    for edge in char_edges:
        edge_map[edge['id']] = edge
    
    # Override with graph.yml edges
    for edge in graph_edges:
        edge_map[edge['id']] = edge
    
    return list(edge_map.values())


def validate_edges(edges: list[dict], valid_ids: set[str], valid_types: list[str]) -> tuple[list[str], list[str]]:
    """Validate edges. Returns (errors, warnings)."""
    errors = []
    warnings = []
    
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        rel_type = edge.get('type', '')
        
        if source not in valid_ids:
            errors.append(f"Edge {edge['id']}: source '{source}' does not exist")
        if target not in valid_ids:
            errors.append(f"Edge {edge['id']}: target '{target}' does not exist")
        if rel_type not in valid_types:
            errors.append(f"Edge {edge['id']}: type '{rel_type}' is not in vocab.yml relationship_types")
    
    return errors, warnings


def validate_tags(characters: list[dict], valid_prefixes: list[str]) -> list[str]:
    """Validate tag prefixes. Returns warnings (not errors per spec)."""
    warnings = []
    
    for char in characters:
        char_id = char.get('id', '')
        tags = char.get('tags', [])
        
        for tag in tags:
            if '/' not in tag:
                warnings.append(f"Character {char_id}: tag '{tag}' not in prefix/value format")
                continue
            
            prefix = tag.split('/')[0]
            if prefix not in valid_prefixes:
                warnings.append(f"Character {char_id}: tag prefix '{prefix}' not in vocab.yml tag_prefixes")
    
    return warnings


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


def build_location_data(locations_dir: Path, maps_dir: Path, links_path: Path, 
                        site_data_dir: Path, character_ids: set[str], vocab: dict):
    """Build location-related JSON files for the site."""
    
    # Load locations
    locations_raw = []
    location_ids = set()
    
    if locations_dir.exists():
        for filepath in sorted(get_location_files(locations_dir)):
            try:
                loc = load_yaml(filepath)
                if loc:
                    locations_raw.append(loc)
                    if 'id' in loc:
                        location_ids.add(loc['id'])
            except Exception as e:
                print(f"WARNING: Failed to load {filepath}: {e}")
    
    # Build locations.json
    locations_json = []
    for loc in locations_raw:
        profile = loc.get('profile', {})
        locations_json.append({
            'id': loc.get('id', ''),
            'name': profile.get('name', ''),
            'short': profile.get('short', ''),
            'type': profile.get('type', ''),
            'parent_id': profile.get('parent_id'),
            'description': profile.get('description', ''),
            'tags': loc.get('tags', []),
            'lore': loc.get('lore', {})
        })
    
    # Write locations.json
    with open(site_data_dir / 'locations.json', 'w', encoding='utf-8') as f:
        json.dump(locations_json, f, ensure_ascii=False, indent=2)
    
    if locations_json:
        print(f"✓ Generated site/data/locations.json ({len(locations_json)} locations)")
    
    # Load and build maps.json
    maps_json = []
    if maps_dir.exists():
        for filepath in sorted(get_map_files(maps_dir)):
            try:
                map_data = load_yaml(filepath)
                if map_data:
                    profile = map_data.get('profile', {})
                    maps_json.append({
                        'id': map_data.get('id', ''),
                        'name': profile.get('name', ''),
                        'description': profile.get('description', ''),
                        'root_location_id': map_data.get('root_location_id', ''),
                        'include': map_data.get('include', {}),
                        'display': map_data.get('display', {})
                    })
            except Exception as e:
                print(f"WARNING: Failed to load {filepath}: {e}")
    
    # Write maps.json
    with open(site_data_dir / 'maps.json', 'w', encoding='utf-8') as f:
        json.dump(maps_json, f, ensure_ascii=False, indent=2)
    
    if maps_json:
        print(f"✓ Generated site/data/maps.json ({len(maps_json)} maps)")
    
    # Load and build character_locations.json
    links_json = []
    if links_path.exists():
        try:
            links_data = load_yaml(links_path)
            if links_data and 'links' in links_data:
                links_json = links_data['links']
        except Exception as e:
            print(f"WARNING: Failed to load character_locations.yml: {e}")
    
    # Write character_locations.json
    with open(site_data_dir / 'character_locations.json', 'w', encoding='utf-8') as f:
        json.dump(links_json, f, ensure_ascii=False, indent=2)
    
    if links_json:
        print(f"✓ Generated site/data/character_locations.json ({len(links_json)} links)")
    
    # Build location graph data for each map
    for map_info in maps_json:
        map_id = map_info.get('id', '')
        root_id = map_info.get('root_location_id', '')
        include = map_info.get('include', {})
        max_depth = include.get('depth', 3)
        allowed_types = include.get('types', [])
        
        if not root_id:
            continue
        
        # Build location tree from root
        loc_by_id = {loc['id']: loc for loc in locations_json}
        
        # Build parent->children mapping for O(1) lookups
        children_by_parent = {}
        for loc in locations_json:
            parent_id = loc.get('parent_id')
            if parent_id not in children_by_parent:
                children_by_parent[parent_id] = []
            children_by_parent[parent_id].append(loc)
        
        # Find all descendants using the prebuilt mapping
        def get_descendants(parent_id, depth):
            if depth > max_depth:
                return []
            result = []
            for loc in children_by_parent.get(parent_id, []):
                if not allowed_types or loc.get('type') in allowed_types:
                    result.append(loc)
                result.extend(get_descendants(loc['id'], depth + 1))
            return result
        
        # Include root if it passes type filter
        graph_locations = []
        if root_id in loc_by_id:
            root_loc = loc_by_id[root_id]
            if not allowed_types or root_loc.get('type') in allowed_types:
                graph_locations.append(root_loc)
        
        graph_locations.extend(get_descendants(root_id, 1))
        
        # Build nodes and edges for this map
        loc_graph_nodes = []
        loc_graph_edges = []
        
        graph_loc_ids = {loc['id'] for loc in graph_locations}
        
        for loc in graph_locations:
            loc_graph_nodes.append({
                'id': loc['id'],
                'label': loc.get('name', loc['id']),
                'type': loc.get('type', ''),
                'tags': loc.get('tags', [])
            })
            
            # Add edge to parent if parent is in graph
            parent_id = loc.get('parent_id')
            if parent_id and parent_id in graph_loc_ids:
                loc_graph_edges.append({
                    'id': f"{parent_id}__contains__{loc['id']}",
                    'source': parent_id,
                    'target': loc['id'],
                    'type': 'contains'
                })
        
        location_graph = {
            'nodes': loc_graph_nodes,
            'edges': loc_graph_edges
        }
        
        # Write location_graph_<map_id>.json
        graph_path = site_data_dir / f'location_graph_{map_id}.json'
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(location_graph, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Generated site/data/location_graph_{map_id}.json ({len(loc_graph_nodes)} nodes)")
        
        # Create layout file if it doesn't exist
        layout_path = site_data_dir / f'location_layout_{map_id}.json'
        if not layout_path.exists():
            with open(layout_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)


def main():
    """Main build function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    characters_dir = repo_root / 'characters'
    locations_dir = repo_root / 'locations'
    maps_dir = repo_root / 'maps'
    links_path = repo_root / 'links' / 'character_locations.yml'
    vocab_path = repo_root / 'schemas' / 'vocab.yml'
    graph_path = repo_root / 'relations' / 'graph.yml'
    site_data_dir = repo_root / 'site' / 'data'
    
    # Ensure output directory exists
    site_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Check required directories/files
    if not characters_dir.exists():
        print("ERROR: characters/ directory not found")
        sys.exit(1)
    
    if not vocab_path.exists():
        print("ERROR: schemas/vocab.yml not found")
        sys.exit(1)
    
    # Load vocab
    try:
        vocab = load_yaml(vocab_path)
    except Exception as e:
        print(f"ERROR: Failed to load vocab.yml: {e}")
        sys.exit(1)
    
    valid_types = vocab.get('relationship_types', [])
    valid_prefixes = vocab.get('tag_prefixes', [])
    
    # Get and load character files
    character_files = get_character_files(characters_dir)
    
    if not character_files:
        print("INFO: No character files found")
        # Write empty data
        with open(site_data_dir / 'characters.json', 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        with open(site_data_dir / 'graph.json', 'w', encoding='utf-8') as f:
            json.dump({'nodes': [], 'edges': []}, f, ensure_ascii=False, indent=2)
        print("✓ Generated empty data files")
        sys.exit(0)
    
    # Load all characters
    characters_raw = []
    for filepath in sorted(character_files):
        try:
            character = load_yaml(filepath)
            if character:
                characters_raw.append(character)
        except Exception as e:
            print(f"WARNING: Failed to load {filepath}: {e}")
    
    valid_ids = {c.get('id') for c in characters_raw if c.get('id')}
    
    # Build characters.json
    characters_json = [extract_character_data(c) for c in characters_raw]
    
    # Validate tags (warnings only)
    tag_warnings = validate_tags(characters_raw, valid_prefixes)
    for warning in tag_warnings:
        print(f"WARNING: {warning}")
    
    # Build graph data
    char_edges = build_edges_from_characters(characters_raw, valid_ids)
    graph_edges = build_edges_from_graph_yml(graph_path, valid_ids, valid_types)
    
    # Merge edges (graph.yml takes precedence)
    all_edges = merge_edges(char_edges, graph_edges)
    
    # Validate edges
    edge_errors, edge_warnings = validate_edges(all_edges, valid_ids, valid_types)
    
    for warning in edge_warnings:
        print(f"WARNING: {warning}")
    
    if edge_errors:
        for error in edge_errors:
            print(f"ERROR: {error}")
        sys.exit(1)
    
    # Build nodes for graph.json
    nodes = []
    for char in characters_raw:
        char_id = char.get('id', '')
        profile = char.get('profile', {})
        name_val = profile.get('name', '')
        
        if isinstance(name_val, dict):
            label = name_val.get('display', name_val.get('full', char_id))
        else:
            label = name_val if name_val else char_id
        
        nodes.append({
            'id': char_id,
            'label': label,
            'tags': char.get('tags', [])
        })
    
    graph_json = {
        'nodes': nodes,
        'edges': all_edges
    }
    
    # Write characters.json
    with open(site_data_dir / 'characters.json', 'w', encoding='utf-8') as f:
        json.dump(characters_json, f, ensure_ascii=False, indent=2)
    
    # Write graph.json
    with open(site_data_dir / 'graph.json', 'w', encoding='utf-8') as f:
        json.dump(graph_json, f, ensure_ascii=False, indent=2)
    
    # Create layout.json if it doesn't exist
    layout_path = site_data_dir / 'layout.json'
    if not layout_path.exists():
        with open(layout_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print(f"✓ Created {layout_path}")
    
    print(f"✓ Generated site/data/characters.json ({len(characters_json)} characters)")
    print(f"✓ Generated site/data/graph.json ({len(nodes)} nodes, {len(all_edges)} edges)")
    
    # === Location System Data Generation ===
    build_location_data(locations_dir, maps_dir, links_path, site_data_dir, valid_ids, vocab)
    
    print(f"✓ Build complete")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
