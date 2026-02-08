# Oh My Skills

> A curated collection of **100+ high-quality agentic skills** from submodules, plus access to **120,000+ skills** from skills.sh for Claude Code, Gemini CLI, Cursor, Copilot, and other AI coding assistants.


## 🚀 Quick Start

### Install Skills via CLI

The easiest way to install individual skills is using the `skills` CLI (powered by [skills.sh](https://skills.sh)):

```bash
# Install a single skill
npx skills add claude-code/claude-skills/algorithmic-art

# Install a skill collection
npx skills add vercel-labs/agent-skills

# Install from this repository
npx skills add oyqsbbe6/oh-my-skills
```

### Install All Skills

For maximum capability, clone this repository to get all skills from all sources:

```bash
# Clone the repository
git clone https://github.com/oyqsbbe6/oh-my-skills.git
cd oh-my-skills

# Initialize all submodules (downloads 120,000+ skills from skills.sh)
git submodule update --init --recursive
```

### Manual Installation

Alternatively, clone this repository and run the download script:

```bash
# Clone the repository
git clone https://github.com/oyqsbbe6/oh-my-skills.git
cd oh-my-skills

# Run the download script (syncs submodules, copies skills, downloads from skills.sh, links to AI tools)
python3 download_good_skills.py

# View the generated index
cat ALL_SKILLS_INDEX.md

# Browse the unified skills collection
ls -la all_skills_collection/
```

### Download All Skills

Use the `download_good_skills.py` script to sync all submodules, copy skills, download from skills.sh, and link to all AI tools:

```bash
# Full workflow (default): sync submodules, copy skills, download top 100 from skills.sh, link to AI tools
python3 download_good_skills.py

# Skip downloading from skills.sh (only use local submodules)
python3 download_good_skills.py --skip-download

# Skip linking to AI tools
python3 download_good_skills.py --skip-link

# Download top 50 instead of 100 from skills.sh
python3 download_good_skills.py --top 50

# Custom output file
python3 download_good_skills.py --output my_skills_index.md

# See all options
python3 download_good_skills.py --help
```

**What this script does:**
1. Syncs all git submodules to latest
2. Scans submodules for skills (finds directories containing `SKILL.md`)
3. Copies local submodule skills to `all_skills_collection/`
4. Fetches top skills from skills.sh
5. Downloads their repositories
6. Copies only the specified skills (ignores others in the same repo)
7. Generates `ALL_SKILLS_INDEX.md` with skill-to-repo mappings
8. Links all AI tools to `all_skills_collection/`

## 📊 Skills Index

After running `download_good_skills.py`, you'll have:

- **`ALL_SKILLS_INDEX.md`** - Complete markdown catalog listing all skills with their source repositories
- **`all_skills_collection/`** - Unified directory containing all skills (linked to all AI tools)

Browse skills by:
- Source repository (submodules vs skills.sh)
- Skill name and description
- GitHub repository links

## 📦 Skill Sources

This repository aggregates skills from multiple high-quality sources:

| Source | Skills | Description |
|--------|--------|-------------|
| **awesome-copilot** | 29 | GitHub Copilot skills and workflows |
| **everything-skills** | 38 | Everything Claude Code skills |
| **claude-skills** | 16 | Official Anthropic skills |
| **superpowers** | 14 | Original Superpowers by Jesse Vincent |
| **planning-with-files** | 12 | Planning and documentation skills |
| **vercel-skills** | 4 | Vercel Labs official skills |
| **ui-ux-pro-max** | 1 | UI/UX design intelligence |

**Total from submodules**: 114+ skills
**Plus skills.sh**: 120,000+ additional skills available via `npx skills add` at [skills.sh](https://skills.sh)

## 🛠️ Usage

### Using Skills with Claude Code

Once installed, use skills naturally in your conversations:

```
Use the architecture skill to help me design a REST API
Run test-driven-development for this feature
Apply react-best-practices to my components
```

### Installing Individual Skills

Browse the skills index or skills.sh, find a skill you want, then install it:

```bash
# From skills.sh (120,000+ skills)
npx skills add <skill-name>

# Examples
npx skills add claude-code/claude-skills/algorithmic-art
npx skills add obra/superpowers/brainstorming
npx skills add vercel-labs/agent-skills
```

### Installing Skill Collections

Install entire collections at once:

```bash
# Official Anthropic skills
npx skills add anthropics/skills

# Vercel Labs skills
npx skills add vercel-labs/agent-skills

# Superpowers
npx skills add obra/superpowers
```

### Using Skills with Other AI Assistants

- **Claude Code**: Skills are automatically loaded from `.claude/skills/`
- **Gemini CLI**: Place skills in `.gemini/skills/`
- **Cursor**: Use `@skill-name` in chat
- **GitHub Copilot**: Paste skill content manually

## 📁 Project Structure

```
oh-my-skills/
├── download_good_skills.py   # Main script to sync, download and link all skills
├── all_skills_collection/    # Unified skills directory (linked to all AI tools)
├── ALL_SKILLS_INDEX.md       # Generated skills catalog with repo mappings
├── dashboard.html            # Interactive skills dashboard
├── skills_sh_downloads/      # Downloaded skills.sh repositories
├── submodules/               # Git submodules containing skill collections
│   ├── awesome-copilot/      # GitHub Copilot skills (29)
│   ├── claude-skills/        # Official Anthropic skills (16)
│   ├── everything-skills/    # Everything Claude skills (38)
│   ├── planning-with-files/  # Planning and documentation skills (12)
│   ├── superpowers/          # Superpowers by obra (14)
│   ├── ui-ux-pro-max/        # UI/UX design skills (1)
│   └── vercel-skills/        # Vercel Labs skills (4)
└── README.md
```

**Note**: This repository contains curated skills from submodules (114+ skills). For the complete skills.sh directory with 120,000+ skills, use `npx skills add` directly or visit [skills.sh](https://skills.sh).

## 🔄 Updating Skills

### Update Skills

To update all skill collections to the latest versions:

```bash
# Run the download script again (will sync all submodules to latest)
python3 download_good_skills.py

# Or manually update submodules only
git submodule update --remote --merge
```

### Browse Latest Skills from skills.sh

skills.sh is constantly updated with new community skills. To browse and install the latest skills:

```bash
# Search for skills
npx skills search <keyword>

# List popular skills
npx skills list --limit 50

# Visit skills.sh website
open https://skills.sh
```

## 🎨 Features

- **Unified Skills Collection** - All skills in one directory (`all_skills_collection/`)
- **Multi-Tool Support** - Automatically links to 30+ AI tools
- **Skills.sh Integration** - Downloads top skills from skills.sh
- **Markdown Index** - Complete catalog with skill-to-repo mappings
- **Submodule Sync** - Keeps all submodules up to date

## 📦 Skill Formats

This repository supports three skill formats:

1. **SKILL.md** - Standard markdown format with YAML frontmatter
2. **skill.json** - JSON format with metadata
3. **metadata.json** - Alternative JSON metadata format

All formats are automatically detected and cataloged.

## 🤝 Contributing

To add new skills to this collection:

1. Fork this repository
2. Add your skill to the appropriate submodule or create a new one
3. Update the submodule references
4. Run `python3 download_good_skills.py` to update the catalog
5. Submit a pull request

## 📄 License

This project is MIT License. Individual skills may have their own licenses - please check each skill's license information.

## 🔗 Related Projects

- [skills.sh](https://skills.sh) - The Agent Skills Directory
- [Agent Skills IO](https://agentskills.io/home) - Agent Skills Platform
- [anthropics/skills](https://github.com/anthropics/skills) - Official Anthropic skills
- [obra/superpowers](https://github.com/obra/superpowers) - Original Superpowers
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) - Vercel Labs skills

## 🌟 Star History

If you find this collection useful, please consider giving it a star!

---

Made with ❤️ by the AI agent community
