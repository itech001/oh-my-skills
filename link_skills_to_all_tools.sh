#!/bin/bash

# Script to create symbolic links from ~/.claude/skills to other AI coding agent tools
# Creates links only if both source and target directories exist

set -e

SOURCE_DIR="$HOME/.claude/skills"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source directory does not exist: $SOURCE_DIR"
    echo "Please create it first: mkdir -p $SOURCE_DIR"
    exit 1
fi

echo "🔗 Creating symbolic links from $SOURCE_DIR to other AI tools..."
echo ""

# Define all tools with their global paths only
declare -A TOOLS=(
    ["amp"]="$HOME/.config/agents/skills"
    ["kimi-cli"]="$HOME/.config/agents/skills"
    ["replit"]="$HOME/.config/agents/skills"
    ["antigravity"]="$HOME/.gemini/antigravity/skills"
    ["augment"]="$HOME/.augment/skills"
    ["claude-code"]="$HOME/.claude/skills"
    ["openclaw"]="$HOME/.moltbot/skills/"
    ["cline"]="$HOME/.cline/skills"
    ["codebuddy"]="$HOME/.codebuddy/skills"
    ["codex"]="$HOME/.codex/skills"
    ["command-code"]="$HOME/.commandcode/skills"
    ["continue"]="$HOME/.continue/skills"
    ["crush"]="$HOME/.config/crush/skills"
    ["cursor"]="$HOME/.cursor/skills"
    ["droid"]="$HOME/.factory/skills"
    ["gemini-cli"]="$HOME/.gemini/skills"
    ["github-copilot"]="$HOME/.copilot/skills"
    ["goose"]="$HOME/.config/goose/skills"
    ["junie"]="$HOME/.junie/skills"
    ["iflow-cli"]="$HOME/.iflow/skills"
    ["kilo"]="$HOME/.kilocode/skills"
    ["kiro-cli"]="$HOME/.kiro/skills"
    ["kode"]="$HOME/.kode/skills"
    ["mcpjam"]="$HOME/.mcpjam/skills"
    ["mistral-vibe"]="$HOME/.vibe/skills"
    ["mux"]="$HOME/.mux/skills"
    ["opencode"]="$HOME/.config/opencode/skills"
    ["openhands"]="$HOME/.openhands/skills"
    ["pi"]="$HOME/.pi/agent/skills"
    ["qoder"]="$HOME/.qoder/skills"
    ["qwen-code"]="$HOME/.qwen/skills"
    ["roo"]="$HOME/.roo/skills"
    ["trae"]="$HOME/.trae/skills"
    ["trae-cn"]="$HOME/.trae-cn/skills"
    ["windsurf"]="$HOME/.codeium/windsurf/skills"
    ["zencoder"]="$HOME/.zencoder/skills"
    ["neovate"]="$HOME/.neovate/skills"
    ["pochi"]="$HOME/.pochi/skills"
    ["adal"]="$HOME/.adal/skills"
)

# Function to check and create symlink
create_symlink() {
    local tool_name="$1"
    local target_dir="$2"
    local source_dir="$3"

    if [ -d "$target_dir" ]; then
        if [ -L "$target_dir" ]; then
            existing_link=$(readlink "$target_dir")
            if [ "$existing_link" = "$source_dir" ]; then
                echo "  ✓ $tool_name: Already linked correctly"
                return
            else
                echo "  ⚠️  $tool_name: Symlink already exists but points to different location ($existing_link)"
                echo "     Skipping. Remove manually to recreate: rm $target_dir"
                return
            fi
        fi

        if [ "$(ls -A "$target_dir" 2>/dev/null)" ]; then
            echo "  ⚠️  $tool_name: Target directory is not empty, skipping to avoid data loss"
            return
        fi

        rmdir "$target_dir" 2>/dev/null || true
        ln -s "$source_dir" "$target_dir"
        echo "  ✓ $tool_name: Created symlink $target_dir -> $source_dir"
    else
        echo "  ⏭️  $tool_name: Target directory does not exist: $target_dir"
    fi
}

# Track statistics
total_tools=0
created_links=0
already_linked=0
target_not_found=0
not_empty=0

# Process each tool
for tool_name in "${!TOOLS[@]}"; do
    target_dir="${TOOLS[$tool_name]}"

    total_tools=$((total_tools + 1))

    # Skip if target is the same as source
    if [ "$target_dir" = "$SOURCE_DIR" ]; then
        continue
    fi

    # Try global path if exists
    if [ -d "$target_dir" ] || [ "$target_dir" = "$HOME/.moltbot/skills/" ]; then
        create_symlink "$tool_name" "$target_dir" "$SOURCE_DIR"
        result=$?
        if [ $result -eq 0 ]; then
            created_links=$((created_links + 1))
        elif [ $result -eq 1 ]; then
            already_linked=$((already_linked + 1))
        elif [ $result -eq 2 ]; then
            not_empty=$((not_empty + 1))
        fi
    else
        echo "  ⏭️  $tool_name: Target directory does not exist: $target_dir"
        target_not_found=$((target_not_found + 1))
    fi
done

# Print summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Total tools checked: $total_tools"
echo "  Symlinks created:    $created_links"
echo "  Already linked:      $already_linked"
echo "  Not empty (skipped):  $not_empty"
echo "  Not found:           $target_not_found"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Done! Your skills are now linked to compatible tools."
echo ""
echo "💡 Tips:"
echo "   - Run this script again after installing new tools"
echo "   - To remove a symlink: rm <target-path>"
echo "   - To re-link: remove the symlink first, then run this script again"
