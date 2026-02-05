# Oh My Skills

> A curated collection of **745+ high-quality agentic skills** for Claude Code, Gemini CLI, Cursor, Copilot, and other AI coding assistants.


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

Alternatively, clone this repository and scan all skills:

```bash
# Clone the repository
git clone https://github.com/oyqsbbe6/oh-my-skills.git
cd oh-my-skills

# Initialize submodules
git submodule update --init --recursive

# Scan and catalog all skills
python3 scan_skills.py

# Open the dashboard
open dashboard.html
```

### Generate Skills Index

Generate a complete Markdown index of all skills:

```bash
# Generate ALL_SKILLS_INDEX.md (default)
python3 integrate_and_download_skills.py

# Generate MD + copy all skills to one directory
python3 integrate_and_download_skills.py --copy

# Generate MD + copy + download skills.sh top 100
python3 integrate_and_download_skills.py --copy --download

# See help for more options
python3 integrate_and_download_skills.py --help
```

See [INTEGRATE_SCRIPT_USAGE.md](INTEGRATE_SCRIPT_USAGE.md) for detailed usage.

## 📊 Skills Dashboard

This repository includes a beautiful **HTML dashboard** with green warming style design to browse and explore all skills:

- **Real-time search** - Find skills by name, description, or tags
- **Source filtering** - Filter by 9 different skill sources
- **Tag filtering** - Browse by popular tags (Python, React, API, Testing, etc.)
- **Statistics** - View total skills and breakdown by source
- **Responsive design** - Works on desktop, tablet, and mobile
- **Automatic tagging** - Skills are automatically tagged with relevant technologies

To use the dashboard:

```bash
# Scan local skills from submodules
python3 scan_skills.py

# Open the interactive dashboard
open dashboard.html
```

Then:
1. Filter by source or tags
2. Search for keywords
3. Install skills using `npx skills add <skill-name>` or use local skill files

**Note**: For 120,000+ additional skills, visit [skills.sh](https://skills.sh) and use `npx skills add <skill-name>`.

## 📦 Skill Sources

This repository aggregates skills from multiple high-quality sources:

| Source | Skills | Description |
|--------|--------|-------------|
| **awesome-skills** | 610 | Antigravity Awesome Skills collection |
| **everything-skills** | 38 | Everything Claude Code skills |
| **awesome-copilot** | 29 | GitHub Copilot skills and workflows |
| **openclaw-skills** | 21 | Community-driven skills for OpenClaw agents |
| **claude-skills** | 16 | Official Anthropic skills |
| **superpowers** | 14 | Original Superpowers by Jesse Vincent |
| **planning-with-files** | 12 | Planning and documentation skills |
| **vercel-skills** | 4 | Vercel Labs official skills |
| **ui-ux-pro-max** | 1 | UI/UX design intelligence |

**Total from submodules**: 745 skills
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

Browse the dashboard, find a skill you want, then install it:

```bash
# From skills.sh (120,000+ skills)
npx skills add <skill-name>

# Examples
npx skills add claude-code/claude-skills/algorithmic-art
npx skills add openclaw/marketing-mode
npx skills add obra/superpowers/brainstorming
```

### Installing Skill Collections

Install entire collections at once:

```bash
# Official Anthropic skills
npx skills add anthropics/skills

# Awesome skills collection
npx skills add sickn33/antigravity-awesome-skills

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
├── scan_skills.py          # Python script to scan local submodules
├── all_skills.json         # Generated skills catalog (745 skills)
├── dashboard.html          # Interactive skills dashboard
├── submodules/             # Git submodules containing skill collections
│   ├── awesome-skills/     # Antigravity awesome skills (610)
│   ├── awesome-copilot/   # GitHub Copilot skills (29)
│   ├── claude-skills/      # Official Anthropic skills (16)
│   ├── everything-skills/   # Everything Claude skills (38)
│   ├── moltbot-skills/     # Moltbot skills (0)
│   ├── openclaw-skills/    # OpenClaw community skills (21)
│   ├── planning-with-files/  # Planning skills (12)

│   ├── superpowers/        # Superpowers by obra (14)
│   ├── ui-ux-pro-max/     # UI/UX design skills (1)
│   └── vercel-skills/      # Vercel Labs skills (4)
└── README.md
```

**Note**: This repository contains curated skills from submodules (745 skills). For the complete skills.sh directory with 120,000+ skills, use `npx skills add` directly or visit [skills.sh](https://skills.sh).

## 🔄 Updating Skills

### Update Submodule Skills

To update all skill collections to the latest versions:

```bash
# Update all submodules
git submodule update --remote --merge

# Re-scan to update catalog
python3 scan_skills.py

# Refresh dashboard
open dashboard.html
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

## 🎨 Dashboard Features

The HTML dashboard includes:

- **Organic Biophilic Design** - Nature-inspired green warming aesthetic
- **Glassmorphism Cards** - Modern frosted glass UI elements
- **Real-time Filtering** - Instant search and filter capabilities
- **Source Badges** - Color-coded badges for each skill source
- **Responsive Grid** - Adaptive layout for all screen sizes
- **Smooth Animations** - Fade-in effects and hover transitions

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
4. Run `python3 scan_skills.py` to update the catalog
5. Submit a pull request

## 📄 License

This project is MIT License. Individual skills may have their own licenses - please check each skill's license information.

## 🔗 Related Projects

- [skills.sh](https://skills.sh) - The Agent Skills Directory
- [anthropics/skills](https://github.com/anthropics/skills) - Official Anthropic skills
- [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) - Awesome skills collection
- [obra/superpowers](https://github.com/obra/superpowers) - Original Superpowers

## 🌟 Star History

If you find this collection useful, please consider giving it a star!

---

Made with ❤️ by the AI agent community
