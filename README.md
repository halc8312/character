# Character Database

A Git-managed story character database designed for AI-powered character portrayal. This repository provides a structured template for defining fictional characters that can be read by AI systems to "act as" those characters.

## Overview

This repository serves as the **Single Source of Truth** for character definitions, with:
- Consistent schema for all characters
- Machine-readable YAML format
- AI portrayal guidelines built-in
- CI validation for data integrity

## Repository Structure

```
.
├── README.md                          # This file
├── schemas/
│   ├── character.schema.json          # JSON Schema for character validation
│   └── vocab.yml                      # Controlled vocabulary (tags, relationship types)
├── characters/
│   └── _TEMPLATE.character.yml        # Template for new characters
├── relations/
│   └── graph.yml                      # Relationship graph (optional centralized view)
├── prompts/
│   ├── system_prompt.md               # AI system prompt
│   └── character_prompt_template.md   # Character-specific prompt template
├── scripts/
│   └── validate_characters.py         # Validation script
└── .github/
    ├── workflows/
    │   └── validate.yml               # CI validation workflow
    ├── ISSUE_TEMPLATE/
    │   └── new_character.yml          # New character proposal template
    └── pull_request_template.md       # PR checklist
```

## Character ID Naming Rules

Character IDs must:
- Use only **lowercase letters**, **numbers**, and **underscores**
- Match the pattern: `^[a-z0-9_]+$`
- Match the filename exactly (e.g., `john_smith.yml` → `id: john_smith`)

**Examples:**
- ✅ `alice_wonder`, `hero_01`, `dark_lord`
- ❌ `Alice-Wonder`, `Hero 01`, `DarkLord`

## Tag System

Tags classify characters using a `prefix/value` format:

```yaml
tags:
  - role/protagonist
  - trait/brave
  - species/human
  - status/alive
```

### Valid Tag Prefixes

| Prefix | Description | Examples |
|--------|-------------|----------|
| `role` | Story role | `protagonist`, `antagonist`, `supporting` |
| `trait` | Personality trait | `brave`, `cunning`, `kind` |
| `species` | Species/race | `human`, `elf`, `android` |
| `origin` | Homeland/origin | `kingdom_a`, `earth` |
| `faction` | Organization | `rebels`, `empire` |
| `status` | Current status | `alive`, `deceased`, `missing` |
| `archetype` | Character archetype | `hero`, `mentor`, `trickster` |
| `power` | Power/magic type | `fire_magic`, `telepathy` |
| `era` | Time period | `medieval`, `future` |
| `genre` | Genre tag | `fantasy`, `scifi`, `modern` |

### Adding New Tag Prefixes

To add a new prefix:
1. Edit `schemas/vocab.yml`
2. Add the prefix to `tag_prefixes` list
3. Optionally add recommended tags to `recommended_tags`
4. Submit a PR

**Validation Behavior:** Tags with invalid prefixes will cause validation errors.

## Relationship System

Relationships are defined in each character's `relationships` array:

```yaml
relationships:
  - target_id: alice_wonder    # Must be existing character ID
    type: friend               # Must be in vocab.yml
    description: "Childhood friends"
    intensity: 4               # -5 (hostile) to 5 (close)
    mutual: true
```

### Valid Relationship Types

| Category | Types |
|----------|-------|
| Family | `parent`, `child`, `sibling`, `spouse`, `relative` |
| Social | `friend`, `rival`, `enemy`, `ally`, `mentor`, `student`, `colleague`, `acquaintance` |
| Romantic | `lover`, `ex_lover`, `crush` |
| Professional | `employer`, `employee`, `partner`, `subordinate`, `superior` |
| Other | `unknown`, `other` |

### Adding New Relationship Types

1. Edit `schemas/vocab.yml`
2. Add the type to `relationship_types` list
3. Submit a PR

### Graph.yml (Optional)

`relations/graph.yml` provides an optional centralized view of relationships. The authoritative source remains each character's `relationships` array. Use `graph.yml` for:
- Visualization tools
- Cross-referencing
- Network analysis

## Adding a New Character

### Step 1: Create Issue (Optional)
Use the [New Character template](.github/ISSUE_TEMPLATE/new_character.yml) to propose the character.

### Step 2: Create Character File
1. Copy `characters/_TEMPLATE.character.yml` to `characters/<your_id>.yml`
2. Replace placeholder values with actual character data
3. Ensure `id` matches the filename

### Step 3: Validate Locally
```bash
# Install dependencies
pip install pyyaml jsonschema

# Run validation
python scripts/validate_characters.py
```

### Step 4: Submit PR
1. Create a branch and commit your changes
2. Open a Pull Request
3. CI will automatically validate
4. Address any issues if validation fails

## Using with AI

### Step 1: Set Up System Prompt

Copy the contents of `prompts/system_prompt.md` as the AI's system prompt. This establishes:
- Character portrayal guidelines
- Boundary rules
- Meta-commentary restrictions
- Safety guidelines

### Step 2: Create Character Prompt

1. Copy `prompts/character_prompt_template.md`
2. Replace `{{CHARACTER_YAML}}` with the full contents of your character's YAML file
3. Use this as the AI's character-specific prompt

### Example Setup

```
[System Prompt]
<contents of prompts/system_prompt.md>

[User/Character Prompt]
<contents of prompts/character_prompt_template.md with {{CHARACTER_YAML}} replaced>

[User Message]
Hello! How are you today?
```

The AI will respond as the character, using their defined voice, personality, and knowledge.

## CI Validation

The GitHub Actions workflow validates on every PR and push to main branches.

### What Gets Checked

| Check | Description |
|-------|-------------|
| **Schema Validation** | All required keys present, correct types |
| **ID/Filename Match** | Character `id` matches the filename |
| **Relationship Targets** | All `target_id` values reference existing characters |
| **Relationship Types** | All `type` values exist in `vocab.yml` |
| **Tag Prefixes** | All tag prefixes exist in `vocab.yml` (error) |
| **Date Formats** | `meta.created` and `meta.updated` are valid YYYY-MM-DD |
| **Graph.yml** | If populated, references valid character IDs and types |

### Running Validation Locally

```bash
pip install pyyaml jsonschema
python scripts/validate_characters.py
```

## Character File Reference

### Required Keys

Every character file must include:

| Key | Description |
|-----|-------------|
| `version` | Schema version (e.g., "1.0") |
| `id` | Unique identifier |
| `profile` | Name, age, gender, role, etc. |
| `tags` | Classification tags |
| `appearance` | Physical description |
| `personality` | Traits, strengths, weaknesses |
| `background` | History and backstory |
| `goals` | Objectives and desires |
| `motivations` | What drives the character |
| `conflicts` | Internal and external conflicts |
| `abilities` | Skills and powers |
| `behavior` | Speech style, mannerisms |
| `secrets` | Hidden information (can be empty `[]`) |
| `relationships` | Connections to other characters (can be empty `[]`) |
| `story` | Role in the narrative |
| `ai_portrayal` | Guidelines and boundaries for AI |
| `meta` | Created/updated dates, author |

See `characters/_TEMPLATE.character.yml` for the full structure with examples.

## Contributing

1. **Characters**: Use the Issue template to propose, then submit a PR
2. **Schema/Vocab Changes**: Discuss in an Issue first
3. **All PRs**: Must pass CI validation

## License

[Add your license here]