#!/usr/bin/env python3
"""
Scan all skills from submodules and save to all_skills.json
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import Counter

def extract_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    lines = match.group(1).split('\n')
    current_key = None
    current_value = []

    for line in lines:
        if ':' in line and not line.startswith(' '):
            # Save previous key-value pair
            if current_key:
                value = '\n'.join(current_value).strip()
                frontmatter[current_key] = value
            # Start new key-value pair
            key, value = line.split(':', 1)
            current_key = key.strip()
            current_value = [value.strip()]
        elif current_key:
            # Continuation of multiline value
            current_value.append(line.strip())

    # Save last key-value pair
    if current_key:
        value = '\n'.join(current_value).strip()
        frontmatter[current_key] = value

    return frontmatter

def extract_tags_from_content(content: str, description: str = '') -> Set[str]:
    """Extract functional tags from skill content and description."""
    tags = set()

    # Tag extraction patterns
    tag_patterns = [
        # Programming languages
        r'\b(Python|JavaScript|TypeScript|Java|C\+\+|C#|Go|Rust|PHP|Ruby|Swift|Kotlin|Scala|R|Haskell|Elixir|Clojure|Dart|Lua|Perl|Bash|Shell)\b',
        # Frameworks & Libraries
        r'\b(React|Vue|Angular|Svelte|Next\.js|Nuxt\.js|Express|FastAPI|Flask|Django|Spring|Laravel|Rails|NestJS)\b',
        r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|D3\.js|Three\.js|p5\.js)\b',
        # Cloud & DevOps
        r'\b(AWS|Azure|GCP|Google Cloud|Docker|Kubernetes|Terraform|Ansible|Jenkins|GitHub Actions|CircleCI)\b',
        r'\b(Netlify|Vercel|Heroku|Cloudflare|Lambda|EC2|S3|ECS|EKS|AKS)\b',
        # Databases
        r'\b(PostgreSQL|MySQL|MongoDB|Redis|Cassandra|Elasticsearch|DynamoDB|CockroachDB)\b',
        r'\b(Firebase|Supabase|PlanetScale|Neon|Prisma|Sequelize|TypeORM)\b',
        # AI/ML
        r'\b(LLM|GPT|Claude|OpenAI|Anthropic|LangChain|LangGraph|Llama|Mistral|Hugging Face)\b',
        r'\b(Embeddings|Vector Search|RAG|Fine-tuning|Prompt Engineering|Agentic)\b',
        # Development Tools
        r'\b(Git|GitHub|GitLab|VS Code|Vim|Emacs|IntelliJ|Webpack|Vite|npm|yarn|pnpm)\b',
        # Testing
        r'\b(Jest|Cypress|Playwright|Selenium|Pytest|Junit|Mocha|Chai|Testing|TDD)\b',
        # Security
        r'\b(Security|Penetration Testing|Bug Bounty|OWASP|Authentication|Authorization|OAuth|JWT)\b',
        # Design
        r'\b(UI|UX|Figma|Sketch|CSS|Tailwind|Bootstrap|Design System|Accessibility|A11y)\b',
        # Mobile
        r'\b(iOS|Android|React Native|Flutter|SwiftUI|Kotlin Compose|Mobile App)\b',
        # Data
        r'\b(Data Science|Data Engineering|ETL|Pipeline|Analytics|Dashboard|Visualization)\b',
        # Web
        r'\b(API|REST|GraphQL|WebSocket|WebRTC|HTTP|HTTPS|HTML|CSS|JavaScript)\b',
        # Block chain
        r'\b(Blockchain|Ethereum|Solidity|Smart Contracts|Web3|DeFi|NFT|Crypto)\b',
    ]

    # Extract tags from patterns
    for pattern in tag_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            tags.add(match)

    # Extract from description as well
    if description:
        for pattern in tag_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                tags.add(match)

    return tags

def scan_skill_md(skill_path: Path, source: str) -> Dict[str, Any]:
    """Scan a SKILL.md file and extract metadata."""
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter = extract_frontmatter(content)
        description = frontmatter.get('description', '')

        # Extract tags automatically
        auto_tags = extract_tags_from_content(content, description)

        # Resolve symlinks to get the actual relative path
        try:
            abs_path = skill_path.resolve()
            rel_path = abs_path.relative_to(Path.cwd().resolve())
        except (ValueError, OSError):
            # Fallback to direct path if resolution fails
            rel_path = str(skill_path)

        # Extract repo name from the skill path
        repo = str(skill_path.parent).split('/')[1] if '/' in str(skill_path.parent) else source

        return {
            'name': frontmatter.get('name', skill_path.parent.name),
            'description': description,
            'source': source,
            'license': frontmatter.get('license', ''),
            'tags': sorted(list(auto_tags)),
            'path': str(rel_path),
            'repo': repo
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

        # Extract repo name from the skill path
        repo = str(skill_path.parent).split('/')[1] if '/' in str(skill_path.parent) else source
        
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
            'repo': repo
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

        # Extract repo name from the skill path
        repo = str(metadata_path.parent).split('/')[1] if '/' in str(metadata_path.parent) else source
        
        return {
            'name': data.get('name', metadata_path.parent.name),
            'description': data.get('description', ''),
            'source': source,
            'license': data.get('license', ''),
            'category': data.get('category', ''),
            'tags': data.get('tags', []),
            'path': str(rel_path),
            'repo': repo
        }
    except Exception as e:
        print(f"Error reading {metadata_path}: {e}")
        return None

def scan_submodule(submodule_path: Path, source: str) -> List[Dict[str, Any]]:
    """Scan a submodule for all skills in 'skills' directories."""
    skills = []

    if not submodule_path.exists():
        print(f"Submodule {submodule_path} does not exist, skipping...")
        return skills

    # Only look in 'skills' directories
    skills_dirs = list(submodule_path.rglob('skills'))

    if not skills_dirs:
        # If no 'skills' directory found, search whole submodule for SKILL.md
        skills_dirs = [submodule_path]

    for skills_dir in skills_dirs:
        # Scan for SKILL.md files directly in skills directories (not nested)
        for skill_md in skills_dir.glob('SKILL.md'):
            skill = scan_skill_md(skill_md, source)
            if skill:
                skills.append(skill)

        # Also scan for SKILL.md in subdirectories of skills/
        for skill_md in skills_dir.rglob('SKILL.md'):
            # Only include if it's in a direct child directory of skills/
            # This avoids nested skills directories
            relative_depth = len(skill_md.relative_to(skills_dir).parts) - 1
            if relative_depth == 1:
                skill = scan_skill_md(skill_md, source)
                if skill and skill['path'] not in [s['path'] for s in skills]:
                    skills.append(skill)

    return skills

def main():
    """Main entry point."""
    submodules = [
        ('submodules/awesome-skills', 'awesome-skills'),
        ('submodules/awesome-copilot', 'awesome-copilot'),
        ('submodules/claude-skills', 'claude-skills'),
        ('submodules/everything-skills', 'everything-skills'),
        ('submodules/moltbot-skills', 'moltbot-skills'),
        ('submodules/openclaw-skills', 'openclaw-skills'),
        ('submodules/planning-with-files', 'planning-with-files'),
        ('submodules/skills-sh-skills', 'skills-sh'),
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
    sources = Counter(skill['source'] for skill in all_skills)
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count}")

    # Print top tags
    print("\n🏷️  Top tags:")
    all_tags = []
    for skill in all_skills:
        all_tags.extend(skill.get('tags', []))
    tag_counter = Counter(all_tags)
    for tag, count in tag_counter.most_common(20):
        print(f"  {tag}: {count}")

if __name__ == '__main__':
    main()
