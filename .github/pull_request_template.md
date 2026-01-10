## Description

<!-- Briefly describe the changes in this PR -->

## Type of Change

- [ ] New character (`characters/<id>.yml`)
- [ ] Character update/edit
- [ ] Schema change
- [ ] Vocabulary update (`vocab.yml`)
- [ ] Documentation update
- [ ] CI/Tooling update
- [ ] Other: <!-- specify -->

## Pre-merge Checklist

### For Character Changes
- [ ] CI validation passes (`validate_characters.py`)
- [ ] Character file follows `_TEMPLATE.character.yml` structure
- [ ] Character ID matches filename (`<id>.yml`)
- [ ] All relationships reference existing character IDs
- [ ] Relationship types are valid (in `vocab.yml`)
- [ ] Tags use valid prefixes (in `vocab.yml`)
- [ ] `meta.updated` date is set to today (YYYY-MM-DD)

### For Schema/Vocabulary Changes
- [ ] Changes are backward compatible (or version is bumped)
- [ ] Existing characters still pass validation
- [ ] README is updated if needed

### General
- [ ] I have tested my changes locally
- [ ] Documentation is updated (if applicable)

## Related Issues

<!-- Link any related issues: Fixes #123, Relates to #456 -->

## Notes for Reviewers

<!-- Any additional context for reviewers -->
