#!/usr/bin/env python3
"""
Scan all skills from submodules and save to all_skills.json
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any

def extract_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter

def scan_skill_md(skill_path: Path, source: str) -> Dict[str, Any]:
    """Scan a SKILL.md file and extract metadata."""
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter = extract_frontmatter(content)

        # Resolve symlinks to get the actual relative path
        try:
            abs_path = skill_path.resolve()
            rel_path = abs_path.relative_to(Path.cwd().resolve())
        except (ValueError, OSError):
            # Fallback to direct path if resolution fails
            rel_path = str(skill_path)

        return {
            'name': frontmatter.get('name', skill_path.parent.name),
            'description': frontmatter.get('description', ''),
            'source': source,
            'license': frontmatter.get('license', ''),
            'path': str(rel_path),
            'type': 'SKILL.md'
        }
    except Exception as e:
        print(f"Error reading {skill_path}: {e}")
        return None

def scan_skill_json(skill_path: Path, source: str) -> Dict[str, Any]:
    """Scan a skill.json file and extract metadata."""
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Resolve symlinks to get the actual relative path
        try:
            abs_path = skill_path.resolve()
            rel_path = abs_path.relative_to(Path.cwd().resolve())
        except (ValueError, OSError):
            # Fallback to direct path if resolution fails
            rel_path = str(skill_path)

        return {
            'name': data.get('name', skill_path.parent.name),
            'description': data.get('description', ''),
            'source': source,
            'license': data.get('license', ''),
            'emoji': data.get('emoji', ''),
            'category': data.get('category', ''),
            'author': data.get('author', ''),
            'version': data.get('version', ''),
            'tags': data.get('tags', []),
            'path': str(rel_path),
            'type': 'skill.json'
        }
    except Exception as e:
        print(f"Error reading {skill_path}: {e}")
        return None

def scan_metadata_json(metadata_path: Path, source: str) -> Dict[str, Any]:
    """Scan a metadata.json file and extract metadata."""
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Resolve symlinks to get the actual relative path
        try:
            abs_path = metadata_path.resolve()
            rel_path = abs_path.relative_to(Path.cwd().resolve())
        except (ValueError, OSError):
            # Fallback to direct path if resolution fails
            rel_path = str(metadata_path)

        return {
            'name': data.get('name', metadata_path.parent.name),
            'description': data.get('description', ''),
            'source': source,
            'license': data.get('license', ''),
            'category': data.get('category', ''),
            'tags': data.get('tags', []),
            'path': str(rel_path),
            'type': 'metadata.json'
        }
    except Exception as e:
        print(f"Error reading {metadata_path}: {e}")
        return None

def scan_submodule(submodule_path: Path, source: str) -> List[Dict[str, Any]]:
    """Scan a submodule for all skills."""
    skills = []

    if not submodule_path.exists():
        print(f"Submodule {submodule_path} does not exist, skipping...")
        return skills

    # Scan for SKILL.md files
    for skill_md in submodule_path.rglob('SKILL.md'):
        skill = scan_skill_md(skill_md, source)
        if skill:
            skills.append(skill)

    # Scan for skill.json files
    for skill_json in submodule_path.rglob('skill.json'):
        skill = scan_skill_json(skill_json, source)
        if skill:
            skills.append(skill)

    # Scan for metadata.json files
    for metadata_json in submodule_path.rglob('metadata.json'):
        # Skip if in node_modules or similar directories
        if 'node_modules' in str(metadata_json):
            continue
        skill = scan_metadata_json(metadata_json, source)
        if skill:
            skills.append(skill)

    return skills

def main():
    """Main entry point."""
    submodules = [
        ('submodules/awesome-skills', 'awesome-skills'),
        ('submodules/claude-skills', 'claude-skills'),
        ('submodules/everything-skills', 'everything-skills'),
        ('submodules/moltbot-skills', 'moltbot-skills'),
        ('submodules/openclaw-skills', 'openclaw-skills'),
        ('submodules/planning-with-files', 'planning-with-files'),
        ('submodules/superpowers', 'superpowers'),
        ('submodules/ui-ux-pro-max', 'ui-ux-pro-max'),
        ('submodules/vercel-skills', 'vercel-skills'),
    ]

    all_skills = []

    for submodule_path, source in submodules:
        print(f"Scanning {source}...")
        skills = scan_submodule(Path(submodule_path), source)
        all_skills.extend(skills)
        print(f"  Found {len(skills)} skills")

    # Sort skills by name
    all_skills.sort(key=lambda x: x['name'].lower())

    # Save to all_skills.json
    output_path = Path('all_skills.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_skills, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Total skills: {len(all_skills)}")
    print(f"✅ Saved to {output_path}")

    # Print statistics by source
    print("\n📊 Skills by source:")
    from collections import Counter
    sources = Counter(skill['source'] for skill in all_skills)
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count}")

if __name__ == '__main__':
    main()
