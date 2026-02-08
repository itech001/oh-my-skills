#!/usr/bin/env python3
"""
同步所有子模块到最新
加载本地技能
获取 skills.sh Top 100
生成 Markdown（含 repo/skills 对应表）
复制本地技能到 all_skills_collection/
下载 skills.sh 仓库
复制 skills.sh 技能到 all_skills_collection/
所有 AI 工具直接链接到 all_skills_collection/
"""

import argparse
import json
import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import subprocess
import sys
import requests
from urllib.parse import urlparse

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()

# 配置
OUTPUT_MD = "ALL_SKILLS_INDEX.md"
SKILLS_OUTPUT_DIR = "all_skills_collection"
SKILLS_SH_DOWNLOADS_DIR = "skills_sh_downloads"
TOP_100_COUNT = 100

# 技能源目录（AI 工具将链接到此目录）
def get_skills_source_dir() -> Path:
    """获取技能源目录路径"""
    return SCRIPT_DIR / SKILLS_OUTPUT_DIR

# AI 工具配置: 工具名称 -> skills 目录路径
AI_TOOLS = {
    "amp": "~/.config/agents/skills",
    "kimi-cli": "~/.config/agents/skills",
    "replit": "~/.config/agents/skills",
    "antigravity": "~/.gemini/antigravity/skills",
    "augment": "~/.augment/skills",
    "claude-code": "~/.claude/skills",
    "openclaw": "~/.moltbot/skills/",
    "cline": "~/.cline/skills",
    "codebuddy": "~/.codebuddy/skills",
    "codex": "~/.codex/skills",
    "command-code": "~/.commandcode/skills",
    "continue": "~/.continue/skills",
    "crush": "~/.config/crush/skills",
    "cursor": "~/.cursor/skills",
    "droid": "~/.factory/skills",
    "gemini-cli": "~/.gemini/skills",
    "github-copilot": "~/.copilot/skills",
    "goose": "~/.config/goose/skills",
    "junie": "~/.junie/skills",
    "iflow-cli": "~/.iflow/skills",
    "kilo": "~/.kilocode/skills",
    "kiro-cli": "~/.kiro/skills",
    "kode": "~/.kode/skills",
    "mcpjam": "~/.mcpjam/skills",
    "mistral-vibe": "~/.vibe/skills",
    "mux": "~/.mux/skills",
    "opencode": "~/.config/opencode/skills",
    "openhands": "~/.openhands/skills",
    "pi": "~/.pi/agent/skills",
    "qoder": "~/.qoder/skills",
    "qwen-code": "~/.qwen/skills",
    "roo": "~/.roo/skills",
    "trae": "~/.trae/skills",
    "trae-cn": "~/.trae-cn/skills",
    "windsurf": "~/.codeium/windsurf/skills",
    "zencoder": "~/.zencoder/skills",
    "neovate": "~/.neovate/skills",
    "pochi": "~/.pochi/skills",
    "adal": "~/.adal/skills",
}

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def run_command(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 120) -> tuple:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def sync_submodules():
    """同步所有子模块到最新版本"""
    print_header("🔄 同步所有子模块到最新")
    
    # 初始化子模块（如果尚未初始化）
    print_info("初始化子模块...")
    success, stdout, stderr = run_command(['git', 'submodule', 'update', '--init', '--recursive'], cwd=SCRIPT_DIR)
    if not success:
        print_warning(f"初始化子模块警告: {stderr}")
    else:
        print_success("子模块初始化完成")
    
    # 获取所有子模块路径
    success, stdout, stderr = run_command(['git', 'submodule', 'foreach', 'pwd'], cwd=SCRIPT_DIR)
    if not success:
        print_error(f"无法获取子模块列表: {stderr}")
        return []
    
    submodule_paths = [p.strip() for p in stdout.strip().split('\n') if p.strip()]
    print_info(f"发现 {len(submodule_paths)} 个子模块")
    
    # 获取子模块名称和 URL 映射
    success, stdout, stderr = run_command(['git', 'config', '--file', '.gitmodules', '--get-regexp', r'submodule\..*\.url'], cwd=SCRIPT_DIR)
    submodule_urls = {}
    if success:
        for line in stdout.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 2:
                # submodule.submodules/name.url -> submodules/name
                name_match = re.search(r'submodule\.(.*?)\.url', parts[0])
                if name_match:
                    submodule_urls[name_match.group(1)] = parts[1]
    
    print_info(f"从 .gitmodules 加载了 {len(submodule_urls)} 个 URL 映射")
    
    updated = 0
    failed = 0
    repo_info = []  # (name, path, url)
    
    for i, path in enumerate(submodule_paths, 1):
        submodule_name = os.path.basename(path)
        # 尝试多种可能的 key 格式
        url = submodule_urls.get(f"submodules/{submodule_name}", "")
        if not url:
            # 尝试直接用 submodule_name 作为 key
            url = submodule_urls.get(submodule_name, "")
        if not url:
            # 尝试找到匹配的 key
            for key in submodule_urls:
                if key.endswith(f"/{submodule_name}"):
                    url = submodule_urls[key]
                    break
        
        print(f"\n[{i}/{len(submodule_paths)}] 更新 {submodule_name}...")
        if url:
            print_info(f"  URL: {url}")
        else:
            print_warning(f"  未找到 URL 映射")
        
        # 进入子模块目录并拉取最新
        success, stdout, stderr = run_command(['git', 'pull', 'origin', 'main'], cwd=Path(path))
        if not success:
            # 尝试 master 分支
            success, stdout, stderr = run_command(['git', 'pull', 'origin', 'master'], cwd=Path(path))
        
        if success:
            print_success(f"  ✓ {submodule_name} 已更新")
            updated += 1
        else:
            # 可能是没有更新或者已经在最新
            if "Already up to date" in stderr or "Already up-to-date" in stdout:
                print_info(f"  ℹ {submodule_name} 已经是最新")
                updated += 1
            else:
                print_warning(f"  ⚠ {submodule_name} 更新失败: {stderr[:100]}")
                failed += 1
        
        repo_info.append((submodule_name, path, url))
    
    print_success(f"\n子模块同步完成: {updated} 个成功, {failed} 个失败")
    return repo_info

def fetch_skills_sh_top100() -> List[Dict]:
    """从 skills.sh 页面抓取 Top 100 技能"""
    print_header(f"🌐 从 skills.sh 获取 Top {TOP_100_COUNT} 技能")
    print_info("正在抓取 skills.sh 页面数据...")
    
    try:
        response = requests.get("https://skills.sh", timeout=30)
        response.raise_for_status()
        html = response.text
        
        skills = []
        
        # 尝试从页面中提取技能数据
        # 查找包含技能名称和仓库的模式
        # 常见模式: owner/repo 格式
        
        # 首先尝试找 JSON 数据
        json_match = re.search(r'window\.__DATA__\s*=\s*(\{.*?\});', html, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if 'skills' in data:
                    skills = data['skills'][:TOP_100_COUNT]
            except:
                pass
        
        # 如果没找到 JSON，尝试从 HTML 解析
        if not skills:
            # 查找技能链接或数据属性
            skill_patterns = [
                r'data-owner="([^"]+)"\s+data-repo="([^"]+)"',
                r'href="/skills/([^/]+)/([^"]+)"',
            ]
            
            for pattern in skill_patterns:
                matches = re.findall(pattern, html)
                for owner, repo in matches:
                    if owner and repo:
                        skills.append({
                            'name': f"{owner}/{repo}",
                            'topSource': f"{owner}/{repo}",
                            'installs': 0
                        })
        
        # 去重
        seen = set()
        unique_skills = []
        for skill in skills:
            key = skill.get('topSource', skill.get('name', ''))
            if key and key not in seen:
                seen.add(key)
                unique_skills.append(skill)
        
        # 限制数量
        unique_skills = unique_skills[:TOP_100_COUNT]
        
        if unique_skills:
            print_success(f"成功获取 {len(unique_skills)} 个技能")
            return unique_skills
        else:
            print_warning("无法从页面解析技能数据，使用内置 Top 100 列表")
            return get_builtin_top100()
            
    except requests.RequestException as e:
        print_error(f"获取 skills.sh 失败: {e}")
        print_info("使用内置 Top 100 列表...")
        return get_builtin_top100()
    except Exception as e:
        print_error(f"解析失败: {e}")
        return get_builtin_top100()

def get_builtin_top100() -> List[Dict]:
    """内置的 Top 100 技能列表（作为备用）"""
    top100 = [
        {"name": "find-skills", "topSource": "vercel-labs/skills", "installs": 142500},
        {"name": "vercel-react-best-practices", "topSource": "vercel-labs/agent-skills", "installs": 103600},
        {"name": "web-design-guidelines", "topSource": "vercel-labs/agent-skills", "installs": 78300},
        {"name": "remotion-best-practices", "topSource": "remotion-dev/skills", "installs": 72600},
        {"name": "frontend-design", "topSource": "anthropics/skills", "installs": 47800},
        {"name": "vercel-composition-patterns", "topSource": "vercel-labs/agent-skills", "installs": 26700},
        {"name": "agent-browser", "topSource": "vercel-labs/agent-browser", "installs": 25000},
        {"name": "skill-creator", "topSource": "anthropics/skills", "installs": 23600},
        {"name": "browser-use", "topSource": "browser-use/browser-use", "installs": 20400},
        {"name": "vercel-react-native-skills", "topSource": "vercel-labs/agent-skills", "installs": 19500},
        {"name": "ui-ux-pro-max", "topSource": "nextlevelbuilder/ui-ux-pro-max-skill", "installs": 16200},
        {"name": "seo-audit", "topSource": "coreyhaines31/marketingskills", "installs": 13600},
        {"name": "audit-website", "topSource": "squirrelscan/skills", "installs": 13000},
        {"name": "supabase-postgres-best-practices", "topSource": "supabase/agent-skills", "installs": 12400},
        {"name": "brainstorming", "topSource": "obra/superpowers", "installs": 11400},
        {"name": "pdf", "topSource": "anthropics/skills", "installs": 10000},
        {"name": "copywriting", "topSource": "coreyhaines31/marketingskills", "installs": 9500},
        {"name": "pptx", "topSource": "anthropics/skills", "installs": 8300},
        {"name": "better-auth-best-practices", "topSource": "better-auth/skills", "installs": 8300},
        {"name": "building-native-ui", "topSource": "expo/skills", "installs": 7900},
        {"name": "xlsx", "topSource": "anthropics/skills", "installs": 7800},
        {"name": "docx", "topSource": "anthropics/skills", "installs": 7800},
        {"name": "marketing-psychology", "topSource": "coreyhaines31/marketingskills", "installs": 7200},
        {"name": "next-best-practices", "topSource": "vercel-labs/next-skills", "installs": 7200},
        {"name": "webapp-testing", "topSource": "anthropics/skills", "installs": 6800},
        {"name": "systematic-debugging", "topSource": "obra/superpowers", "installs": 6400},
        {"name": "mcp-builder", "topSource": "anthropics/skills", "installs": 6300},
        {"name": "programmatic-seo", "topSource": "coreyhaines31/marketingskills", "installs": 6200},
        {"name": "marketing-ideas", "topSource": "coreyhaines31/marketingskills", "installs": 5600},
        {"name": "test-driven-development", "topSource": "obra/superpowers", "installs": 5600},
        {"name": "writing-plans", "topSource": "obra/superpowers", "installs": 5500},
        {"name": "canvas-design", "topSource": "anthropics/skills", "installs": 5500},
        {"name": "pricing-strategy", "topSource": "coreyhaines31/marketingskills", "installs": 5200},
        {"name": "upgrading-expo", "topSource": "expo/skills", "installs": 5200},
        {"name": "social-content", "topSource": "coreyhaines31/marketingskills", "installs": 5200},
        {"name": "native-data-fetching", "topSource": "expo/skills", "installs": 5200},
        {"name": "vue-best-practices", "topSource": "hyf0/vue-skills", "installs": 5100},
        {"name": "executing-plans", "topSource": "obra/superpowers", "installs": 5000},
        {"name": "copy-editing", "topSource": "coreyhaines31/marketingskills", "installs": 4800},
        {"name": "page-cro", "topSource": "coreyhaines31/marketingskills", "installs": 4600},
        {"name": "launch-strategy", "topSource": "coreyhaines31/marketingskills", "installs": 4600},
        {"name": "expo-dev-client", "topSource": "expo/skills", "installs": 4600},
        {"name": "doc-coauthoring", "topSource": "anthropics/skills", "installs": 4500},
        {"name": "requesting-code-review", "topSource": "obra/superpowers", "installs": 4500},
        {"name": "expo-tailwind-setup", "topSource": "expo/skills", "installs": 4500},
        {"name": "theme-factory", "topSource": "anthropics/skills", "installs": 4500},
        {"name": "analytics-tracking", "topSource": "coreyhaines31/marketingskills", "installs": 4500},
        {"name": "expo-deployment", "topSource": "expo/skills", "installs": 4500},
        {"name": "remembering-conversations", "topSource": "obra/episodic-memory", "installs": 4500},
        {"name": "schema-markup", "topSource": "coreyhaines31/marketingskills", "installs": 4400},
        {"name": "onboarding-cro", "topSource": "coreyhaines31/marketingskills", "installs": 4400},
        {"name": "subagent-driven-development", "topSource": "obra/superpowers", "installs": 4400},
        {"name": "web-artifacts-builder", "topSource": "anthropics/skills", "installs": 4400},
        {"name": "competitor-alternatives", "topSource": "coreyhaines31/marketingskills", "installs": 4300},
        {"name": "expo-api-routes", "topSource": "expo/skills", "installs": 4300},
        {"name": "clawdirect", "topSource": "napoleond/clawdirect", "installs": 4300},
        {"name": "react-native-best-practices", "topSource": "callstackincubator/agent-skills", "installs": 4300},
        {"name": "instaclaw", "topSource": "napoleond/instaclaw", "installs": 4300},
        {"name": "paid-ads", "topSource": "coreyhaines31/marketingskills", "installs": 4200},
        {"name": "email-sequence", "topSource": "coreyhaines31/marketingskills", "installs": 4200},
        {"name": "clawdirect-dev", "topSource": "napoleond/clawdirect", "installs": 4200},
        {"name": "using-superpowers", "topSource": "obra/superpowers", "installs": 4100},
        {"name": "verification-before-completion", "topSource": "obra/superpowers", "installs": 4100},
        {"name": "algorithmic-art", "topSource": "anthropics/skills", "installs": 4100},
        {"name": "writing-skills", "topSource": "obra/superpowers", "installs": 4100},
        {"name": "using-git-worktrees", "topSource": "obra/superpowers", "installs": 4100},
        {"name": "free-tool-strategy", "topSource": "coreyhaines31/marketingskills", "installs": 4000},
        {"name": "brand-guidelines", "topSource": "anthropics/skills", "installs": 4000},
        {"name": "signup-flow-cro", "topSource": "coreyhaines31/marketingskills", "installs": 4000},
        {"name": "tailwind-design-system", "topSource": "wshobson/agents", "installs": 4000},
        {"name": "receiving-code-review", "topSource": "obra/superpowers", "installs": 3900},
        {"name": "template-skill", "topSource": "anthropics/skills", "installs": 3900},
        {"name": "paywall-upgrade-cro", "topSource": "coreyhaines31/marketingskills", "installs": 3900},
        {"name": "referral-program", "topSource": "coreyhaines31/marketingskills", "installs": 3900},
        {"name": "form-cro", "topSource": "coreyhaines31/marketingskills", "installs": 3800},
        {"name": "dispatching-parallel-agents", "topSource": "obra/superpowers", "installs": 3800},
        {"name": "internal-comms", "topSource": "anthropics/skills", "installs": 3800},
        {"name": "expo-cicd-workflows", "topSource": "expo/skills", "installs": 3800},
        {"name": "popup-cro", "topSource": "coreyhaines31/marketingskills", "installs": 3800},
        {"name": "ab-test-setup", "topSource": "coreyhaines31/marketingskills", "installs": 3700},
        {"name": "use-dom", "topSource": "expo/skills", "installs": 3700},
        {"name": "slack-gif-creator", "topSource": "anthropics/skills", "installs": 3600},
        {"name": "finishing-a-development-branch", "topSource": "obra/superpowers", "installs": 3500},
        {"name": "create-auth-skill", "topSource": "better-auth/skills", "installs": 3400},
        {"name": "ai-sdk", "topSource": "vercel/ai", "installs": 3400},
        {"name": "typescript-advanced-types", "topSource": "wshobson/agents", "installs": 3400},
        {"name": "vue", "topSource": "antfu/skills", "installs": 3400},
        {"name": "vite", "topSource": "antfu/skills", "installs": 3400},
        {"name": "shadcn-ui", "topSource": "giuseppe-trisciuoglio/developer-kit", "installs": 3300},
        {"name": "turborepo", "topSource": "vercel/turborepo", "installs": 3200},
        {"name": "ralph-tui-prd", "topSource": "subsy/ralph-tui", "installs": 3200},
        {"name": "react:components", "topSource": "google-labs-code/stitch-skills", "installs": 3100},
        {"name": "vitest", "topSource": "antfu/skills", "installs": 3000},
        {"name": "design-md", "topSource": "google-labs-code/stitch-skills", "installs": 3000},
        {"name": "vue-best-practices-v2", "topSource": "antfu/skills", "installs": 3000},
        {"name": "api-design-principles", "topSource": "wshobson/agents", "installs": 3000},
        {"name": "pnpm", "topSource": "antfu/skills", "installs": 2800},
        {"name": "ralph-tui-create-json", "topSource": "subsy/ralph-tui", "installs": 2800},
        {"name": "vueuse-functions", "topSource": "antfu/skills", "installs": 2800},
        {"name": "pinia", "topSource": "antfu/skills", "installs": 2700},
    ]
    print_success(f"使用内置列表: {len(top100)} 个技能")
    return top100

def generate_markdown(repo_skills: Dict[str, List[Path]], skills_sh_skills: List[Dict], repo_info: List[Tuple[str, str, str]]) -> str:
    """生成 Markdown 目录"""

    print_info("生成 Markdown 目录...")
    
    # 计算本地技能总数
    total_local_skills = sum(len(skills) for skills in repo_skills.values())
    
    # 构建本地技能名称到repo的映射
    local_skill_to_repo = {}
    for repo_name, skill_dirs in repo_skills.items():
        repo_url = ""
        for name, path, url in repo_info:
            if name == repo_name:
                repo_url = url
                break
        for skill_dir in skill_dirs:
            local_skill_to_repo[skill_dir.name] = (repo_name, repo_url)

    # 生成 Markdown - 简洁清晰的格式
    md_content = f"""# 全部技能目录整合

> 生成时间: {subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()}

## 📊 统计概览

| 类别 | 技能数量 |
|------|---------|
| **本地 Submodules 技能** | {total_local_skills:,} |
| **Skills.sh Top {TOP_100_COUNT}** | {len(skills_sh_skills):,} |
| **总计** | {total_local_skills + len(skills_sh_skills):,} |

---

## 📋 本地 Submodules 技能 ({total_local_skills} 个)

| 技能名称 | 来源仓库 | GitHub 地址 |
|---------|---------|------------|
"""

    # 添加本地技能列表 - 按字母排序
    for skill_name in sorted(local_skill_to_repo.keys()):
        repo_name, repo_url = local_skill_to_repo[skill_name]
        display_url = repo_url.replace('https://github.com/', '') if repo_url else 'N/A'
        md_content += f"| `{skill_name}` | `{repo_name}` | [{display_url}]({repo_url}) |\n"

    # 添加 skills.sh 技能列表
    md_content += f"""

---

## 🌟 Skills.sh Top {len(skills_sh_skills)} 技能

| 排名 | 技能名称 | 安装量 | 来源仓库 |
|------|---------|--------|----------|
"""

    for i, skill in enumerate(skills_sh_skills, 1):
        name = skill.get('name', 'unknown')
        installs = skill.get('installs', 0)
        source = skill.get('topSource', skill.get('source', 'unknown'))
        md_content += f"| {i} | `{name}` | {installs:,} | `{source}` |\n"

    # 添加仓库分组汇总
    md_content += f"""

---

## 📁 按仓库分组的技能列表

"""

    # 本地子模块分组
    if repo_skills:
        md_content += "### 本地子模块\n\n"
        for repo_name in sorted(repo_skills.keys()):
            skills = repo_skills[repo_name]
            repo_url = ""
            for name, path, url in repo_info:
                if name == repo_name:
                    repo_url = url
                    break
            
            display_url = repo_url.replace('https://github.com/', '') if repo_url else 'N/A'
            md_content += f"- **{repo_name}** ([{display_url}]({repo_url})): "
            md_content += ", ".join([f"`{s.name}`" for s in skills])
            md_content += "\n"

    # skills.sh 仓库分组
    md_content += "\n### Skills.sh 仓库\n\n"
    
    # 按仓库分组统计 skills.sh 技能
    from collections import defaultdict
    repo_to_skills = defaultdict(list)
    for skill in skills_sh_skills:
        name = skill.get('name', '')
        source = skill.get('topSource', skill.get('source', ''))
        if name and source:
            repo_to_skills[source].append(name)
    
    for repo_name in sorted(repo_to_skills.keys()):
        skills = repo_to_skills[repo_name]
        md_content += f"- **`{repo_name}`**: "
        md_content += ", ".join([f"`{s}`" for s in skills])
        md_content += "\n"

    md_content += """

---

## 📥 安装方式

### 安装单个技能

```bash
# 从 skills.sh 安装
npx skills add <owner>/<repo>

# 示例
npx skills add anthropics/skills
npx skills add vercel-labs/agent-skills
```

### 安装技能集合

```bash
# 本地技能已经包含在 submodules 中
# 无需额外安装，Claude Code 会自动加载

# 或安装完整的技能集合
npx skills add oyqsbbe6/oh-my-skills
```

### 使用技能

在 Claude Code 中直接引用技能：

```
使用 react-best-practices 技能来优化我的组件
运行 architecture 技能来设计 REST API
```

---

## 🔗 相关链接

- [skills.sh](https://skills.sh) - 技能目录平台
- [本项目 GitHub](https://github.com/oyqsbbe6/oh-my-skills)
- [Claude Code 文档](https://docs.anthropic.com/claude-code)

---

*此文件由 `download_good_skills.py` 自动生成*
"""

    return md_content

def save_markdown(content: str, filename: str = OUTPUT_MD):
    """保存 Markdown 文件"""
    output_path = SCRIPT_DIR / filename
    print_info(f"保存 Markdown 文件到 {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print_success(f"Markdown 文件已保存: {output_path}")

def scan_submodules_for_skills(repo_info: List[Tuple[str, str, str]]) -> Dict[str, List[Path]]:
    """扫描所有子模块，查找包含 SKILL.md 的技能目录
    返回: {repo_name: [skill_dir_paths]}
    """
    print_header("🔍 扫描子模块中的 Skills")
    
    repo_skills = {}
    total_skills = 0
    
    for repo_name, repo_path, repo_url in repo_info:
        print(f"\n  扫描 {repo_name}...")
        print_info(f"    路径: {repo_path}")
        
        repo_path_obj = Path(repo_path)
        
        if not repo_path_obj.exists():
            print_warning(f"    仓库路径不存在: {repo_path}")
            continue
        
        # 检查路径是否是目录
        if not repo_path_obj.is_dir():
            print_warning(f"    路径不是目录: {repo_path}")
            continue
        
        # 查找所有包含 SKILL.md 的目录
        skill_dirs = find_skill_dirs(repo_path_obj)
        
        if skill_dirs:
            repo_skills[repo_name] = skill_dirs
            total_skills += len(skill_dirs)
            print_success(f"    发现 {len(skill_dirs)} 个技能")
            for skill_dir in skill_dirs:
                print(f"      - {skill_dir.name}")
        else:
            print_info(f"    未发现技能 (检查了 {repo_path_obj})")
            # 调试：列出目录内容
            try:
                subdirs = [d.name for d in repo_path_obj.iterdir() if d.is_dir()]
                if subdirs:
                    print_info(f"    目录包含: {', '.join(subdirs[:5])}")
            except Exception as e:
                print_warning(f"    无法列出目录: {e}")
    
    print_success(f"\n扫描完成: 共 {total_skills} 个技能来自 {len(repo_skills)} 个仓库")
    return repo_skills

def copy_local_skills(repo_skills: Dict[str, List[Path]], output_dir: Path) -> int:
    """复制本地技能到统一目录"""
    print_header("📦 复制本地子模块技能")

    output_dir.mkdir(exist_ok=True)
    print_info(f"目标目录: {output_dir.absolute()}")

    copied = 0
    skipped = 0
    
    for repo_name, skill_dirs in repo_skills.items():
        print(f"\n  复制 {repo_name} 的技能...")
        
        for skill_dir in skill_dirs:
            # 技能名称使用目录名
            skill_name = skill_dir.name
            dest_dir = output_dir / skill_name

            # 如果已存在，添加前缀
            counter = 1
            original_dest = dest_dir
            while dest_dir.exists():
                dest_dir = output_dir / f"{skill_name}_{counter}"
                counter += 1

            try:
                # 复制整个目录
                shutil.copytree(skill_dir, dest_dir)
                copied += 1
                
                if original_dest != dest_dir:
                    print_success(f"    ✓ {skill_name} (重命名为 {dest_dir.name})")
                else:
                    print_success(f"    ✓ {skill_name}")

                if copied % 50 == 0:
                    print_info(f"  进度: 已复制 {copied} 个技能...")

            except Exception as e:
                print_error(f"    ✗ 复制失败 {skill_name}: {e}")
                skipped += 1

    print_success(f"\n本地技能复制完成: {copied} 个成功, {skipped} 个跳过")
    return copied

def get_github_url(skill: Dict) -> Optional[str]:
    """从 skill 信息中提取 GitHub repo URL"""
    # 尝试从多个字段获取 repo 信息
    top_source = skill.get('topSource', skill.get('repo', skill.get('repository', '')))

    if top_source and '/' in top_source:
        # 格式: owner/repo
        return f"https://github.com/{top_source}"

    # 如果没有明确的 repo 信息，尝试从其他字段获取
    repo = skill.get('repo', skill.get('repository', ''))
    if repo:
        if repo.startswith('http'):
            return repo
        if '/' in repo:
            return f"https://github.com/{repo}"

    return None

def clone_repo(github_url: str, dest_dir: Path) -> bool:
    """克隆 GitHub 仓库到指定目录"""
    try:
        cmd = ['git', 'clone', '--depth', '1', github_url, str(dest_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0
    except Exception:
        return False

def find_skill_dirs(repo_dir: Path) -> List[Path]:
    """
    在仓库中查找技能目录
    Skill 定义为：包含 SKILL.md 文件的目录
    返回包含 SKILL.md 的目录路径列表
    """
    skill_dirs = []
    
    if not repo_dir.exists():
        print_warning(f"      仓库不存在: {repo_dir}")
        return skill_dirs
    
    # 使用 rglob 查找所有 SKILL.md 文件
    skill_md_files = list(repo_dir.rglob("SKILL.md"))
    print_info(f"      找到 {len(skill_md_files)} 个 SKILL.md 文件")
    
    for skill_md in skill_md_files:
        # 跳过 .git 目录下的文件
        if ".git" in str(skill_md):
            continue
        
        # 获取包含 SKILL.md 的目录
        skill_dir = skill_md.parent
        skill_dirs.append(skill_dir)
    
    return skill_dirs

def download_skills_sh_repos(skills_sh_skills: List[Dict]) -> Tuple[Dict[str, Path], Dict[str, str]]:
    """
    从 skills.sh 下载技能仓库到本地
    返回: (repo_name -> repo_path 映射, skill_name -> repo_name 映射)
    """
    print_header("⬇️ 下载 Skills.sh Top 100 仓库")

    downloads_dir = SCRIPT_DIR / SKILLS_SH_DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)

    print_info(f"下载目录: {downloads_dir.absolute()}")
    
    # 获取唯一的仓库列表，同时记录每个 skill 属于哪个 repo
    repos_to_download: Dict[str, str] = {}  # repo_name -> github_url
    skill_to_repo: Dict[str, str] = {}  # skill_name -> repo_name
    
    for skill in skills_sh_skills:
        skill_name = skill.get('name', '')
        github_url = get_github_url(skill)
        if github_url:
            # 提取 repo_name
            parts = github_url.replace('https://github.com/', '').split('/')
            if len(parts) >= 2:
                # 使用 owner-repo 格式
                repo_name = f"{parts[0]}-{parts[1]}"
                if repo_name not in repos_to_download:
                    repos_to_download[repo_name] = github_url
                # 记录 skill 到 repo 的映射
                if skill_name:
                    skill_to_repo[skill_name] = repo_name
    
    print_info(f"发现 {len(repos_to_download)} 个唯一仓库需要下载")
    print_info(f"涉及 {len(skill_to_repo)} 个特定技能")

    downloaded_repos: Dict[str, Path] = {}  # repo_name -> repo_path
    failed = 0
    skipped = 0

    for i, (repo_name, github_url) in enumerate(sorted(repos_to_download.items()), 1):
        dest_dir = downloads_dir / repo_name

        # 如果已存在，跳过
        if dest_dir.exists():
            print_info(f"[{i}/{len(repos_to_download)}] 跳过 {repo_name} - 已存在")
            downloaded_repos[repo_name] = dest_dir
            skipped += 1
            continue

        print(f"\n[{i}/{len(repos_to_download)}] 下载 {repo_name}...")
        print(f"  URL: {github_url}")

        try:
            if clone_repo(github_url, dest_dir):
                downloaded_repos[repo_name] = dest_dir
                print_success(f"✓ 下载成功: {repo_name}")
            else:
                failed += 1
                print_error(f"✗ 下载失败: {repo_name}")

        except Exception as e:
            failed += 1
            print_error(f"✗ 异常: {repo_name} - {e}")

        # 每 5 个显示进度
        if i % 5 == 0:
            print_info(f"进度: {i}/{len(repos_to_download)}, 成功: {len(downloaded_repos)}, 失败: {failed}, 跳过: {skipped}")

    print_success(f"\n下载完成: {len(downloaded_repos)} 个成功, {failed} 个失败, {skipped} 个已存在")
    return downloaded_repos, skill_to_repo

def copy_skills_from_repos(repos: Dict[str, Path], skill_to_repo: Dict[str, str], output_dir: Path) -> Tuple[int, Dict[str, str]]:
    """
    从下载的仓库中复制特定的技能到统一目录
    只复制在 skills.sh 列表中的技能，忽略 repo 中的其他技能
    返回: (复制数量, skill_name -> repo_name 映射)
    """
    print_header("📋 从下载的仓库复制指定技能")
    
    output_dir.mkdir(exist_ok=True)
    print_info(f"目标目录: {output_dir.absolute()}")
    print_info(f"将复制 {len(skill_to_repo)} 个指定技能\n")

    total_copied = 0
    failed = 0
    copied_skills: Dict[str, str] = {}  # 记录成功复制的 skill -> repo

    # 对于每个 repo，只查找并复制指定的 skills
    for repo_name, repo_path in sorted(repos.items()):
        # 获取该 repo 需要复制的 skills
        skills_in_repo = {s: r for s, r in skill_to_repo.items() if r == repo_name}
        
        if not skills_in_repo:
            continue
        
        print(f"  {repo_name}: 需要复制 {len(skills_in_repo)} 个技能")
        
        # 在 repo 中查找所有 skill 目录
        all_skill_dirs = find_skill_dirs(repo_path)
        
        # 创建 skill_name -> skill_dir 的映射
        skill_dir_map = {d.name: d for d in all_skill_dirs}
        
        # 只复制指定的 skills
        for skill_name in skills_in_repo:
            if skill_name in skill_dir_map:
                skill_dir = skill_dir_map[skill_name]
                dest_dir = output_dir / skill_name
                
                # 如果已存在，添加前缀
                counter = 1
                original_dest = dest_dir
                original_name = skill_name
                while dest_dir.exists():
                    skill_name = f"{original_name}_{counter}"
                    dest_dir = output_dir / skill_name
                    counter += 1
                
                try:
                    shutil.copytree(skill_dir, dest_dir)
                    total_copied += 1
                    copied_skills[original_name] = repo_name
                    
                    if original_dest != dest_dir:
                        print_success(f"    ✓ {original_name} (重命名为 {skill_name})")
                    else:
                        print_success(f"    ✓ {original_name}")
                except Exception as e:
                    print_error(f"    ✗ 复制失败 {original_name}: {e}")
                    failed += 1
            else:
                print_warning(f"    ⚠ {skill_name}: 在仓库中未找到")
                failed += 1
    
    print_success(f"\n技能复制完成: {total_copied} 个成功, {failed} 个失败")
    return total_copied, copied_skills

def link_skills_to_ai_tools():
    """将技能链接到所有 AI 工具（创建符号链接）"""
    print_header("🔗 链接技能到所有 AI 工具")
    
    skills_source_dir = get_skills_source_dir()
    
    # 确保源目录存在
    if not skills_source_dir.exists():
        print_warning(f"技能源目录不存在: {skills_source_dir}")
        print_info("请先运行脚本复制技能到 all_skills_collection/")
        return
    
    print_info(f"技能源目录: {skills_source_dir}")
    print_info(f"将为 {len(AI_TOOLS)} 个 AI 工具创建符号链接\n")
    
    created = 0
    already_linked = 0
    failed = 0
    
    for tool_name, target_path in sorted(AI_TOOLS.items()):
        target_dir = Path(target_path).expanduser()
        
        # 跳过与源目录相同的（避免自链接）
        if target_dir == skills_source_dir:
            continue
        
        try:
            # 创建父目录
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查现有的符号链接
            if target_dir.is_symlink():
                existing_link = target_dir.readlink()
                if existing_link == skills_source_dir:
                    print_success(f"  ✓ {tool_name}: 已正确链接")
                    already_linked += 1
                    continue
                else:
                    # 删除错误的链接
                    target_dir.unlink()
                    print_warning(f"  ℹ {tool_name}: 替换旧链接 ({existing_link})")
            
            # 如果存在目录或文件，删除它
            if target_dir.exists():
                if target_dir.is_dir():
                    shutil.rmtree(target_dir)
                else:
                    target_dir.unlink()
                print_warning(f"  ℹ {tool_name}: 移除已存在的目录/文件")
            
            # 创建符号链接
            target_dir.symlink_to(skills_source_dir)
            print_success(f"  ✓ {tool_name}: 创建链接 {target_dir} -> {skills_source_dir}")
            created += 1
            
        except Exception as e:
            print_error(f"  ✗ {tool_name}: 失败 - {e}")
            failed += 1
    
    print_success(f"\n链接完成: {created} 个创建, {already_linked} 个已存在, {failed} 个失败")
    
    # 打印链接状态摘要
    print_header("📋 链接状态摘要")
    for tool_name, target_path in sorted(AI_TOOLS.items()):
        target_dir = Path(target_path).expanduser()
        
        if target_dir.is_symlink():
            existing_link = target_dir.readlink()
            if existing_link == skills_source_dir:
                print_success(f"  ✓ {tool_name}")
                print(f"    -> {target_dir}")
            else:
                print_warning(f"  ⚠ {tool_name}")
                print(f"    -> {target_dir} -> {existing_link} (不同目标)")
        elif target_dir.exists():
            print_warning(f"  ⚠ {tool_name}")
            print(f"    -> {target_dir} (不是符号链接)")
        else:
            print_error(f"  ✗ {tool_name}")
            print(f"    -> {target_dir} (未链接)")

def create_collection_readme():
    """创建集合目录的 README"""
    readme_content = f"""# 全部技能集合

这个目录包含了从各个来源整合的所有技能。

## 目录结构

- `{SKILLS_OUTPUT_DIR}/` - 所有技能的统一目录
  - 本地 submodules 技能（复制）
  - skills.sh 技能（下载后复制）

## 使用方法

这些技能可以：
1. 直接被 Claude Code 使用
2. 作为参考和学习的资源
3. 复制到其他项目中

## 更新

运行 `python3 download_good_skills.py` 来更新此集合。

---
*由 download_good_skills.py 自动生成*
"""

    output_dir = SCRIPT_DIR / SKILLS_OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)
    readme_path = output_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print_success(f"创建 README: {readme_path}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='整合所有技能并生成 Markdown 目录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 完整流程（默认）
  %(prog)s --skip-download    # 跳过下载 skills.sh 仓库
  %(prog)s --skip-link        # 跳过链接到 AI 工具
  %(prog)s --top 50           # 只下载前 50 个技能相关的仓库
        """
    )

    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='跳过下载 skills.sh 仓库'
    )
    
    parser.add_argument(
        '--skip-copy-skills',
        action='store_true',
        help='下载仓库但不复制其中的技能'
    )
    
    parser.add_argument(
        '--skip-link',
        action='store_true',
        help='跳过链接到 AI 工具'
    )

    parser.add_argument(
        '--top', '-n',
        type=int,
        default=TOP_100_COUNT,
        metavar='N',
        help=f'下载 skills.sh 前 N 个技能相关的仓库（默认: {TOP_100_COUNT}）'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default=OUTPUT_MD,
        help=f'输出 Markdown 文件名（默认: {OUTPUT_MD}）'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='安静模式，减少输出信息'
    )

    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()

    if not args.quiet:
        print_header("🚀 技能整合与下载工具")

    # 1. 同步子模块（默认执行）
    repo_info = sync_submodules()

    # 2. 扫描子模块中的技能（通过查找 SKILL.md）
    repo_skills = scan_submodules_for_skills(repo_info)
    
    total_local_skills = sum(len(skills) for skills in repo_skills.values())
    if total_local_skills == 0:
        print_warning("未在子模块中发现任何技能")

    # 3. 从 skills.sh 获取 Top 100
    skills_sh_skills = fetch_skills_sh_top100()
    
    # 限制数量
    skills_sh_skills = skills_sh_skills[:args.top]

    # 4. 生成 Markdown（包含仓库信息）
    md_content = generate_markdown(repo_skills, skills_sh_skills, repo_info)
    save_markdown(md_content, args.output)

    # 5. 复制本地技能（默认执行）
    output_dir = SCRIPT_DIR / SKILLS_OUTPUT_DIR
    copy_local_skills(repo_skills, output_dir)

    # 6. 下载 skills.sh 仓库（默认执行，可用 --skip-download 跳过）
    downloaded_repos = {}
    skill_to_repo = {}
    skills_sh_copied = {}
    if not args.skip_download and skills_sh_skills:
        downloaded_repos, skill_to_repo = download_skills_sh_repos(skills_sh_skills)
        
        # 7. 从下载的仓库复制技能（默认执行，只复制指定的 skills）
        if not args.skip_copy_skills and downloaded_repos:
            _, skills_sh_copied = copy_skills_from_repos(downloaded_repos, skill_to_repo, output_dir)
        elif downloaded_repos:
            print_info("跳过从下载仓库复制技能")
    else:
        print_info("跳过下载 skills.sh 仓库")

    # 创建 README
    create_collection_readme()
    
    # 8. 链接到所有 AI 工具（默认执行，可用 --skip-link 跳过）
    if not args.skip_link:
        link_skills_to_ai_tools()
    else:
        print_info("跳过链接到 AI 工具")

    # 完成
    if not args.quiet:
        print_header("✅ 完成")

        print_success(f"✓ Markdown 目录已生成: {args.output}")
        print_success(f"✓ 本地技能已复制到: {SKILLS_OUTPUT_DIR}/")
        
        if not args.skip_download and skills_sh_skills:
            print_success(f"✓ Skills.sh 仓库已下载到: {SKILLS_SH_DOWNLOADS_DIR}/")
            if not args.skip_copy_skills:
                print_success(f"✓ Skills.sh 技能已复制到: {SKILLS_OUTPUT_DIR}/")
        
        if not args.skip_link:
            print_success(f"✓ 技能已链接到 {len(AI_TOOLS)} 个 AI 工具")

        print_info(f"\n查看目录: cat {args.output}")
        print_info(f"浏览技能: ls -la {SKILLS_OUTPUT_DIR}/\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
