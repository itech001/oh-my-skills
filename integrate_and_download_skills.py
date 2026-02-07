#!/usr/bin/env python3
"""
整合所有技能并生成 Markdown 目录
同时下载所有技能到统一目录
"""

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import List, Dict
import subprocess
import sys

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()

# 配置
OUTPUT_MD = "ALL_SKILLS_INDEX.md"
SKILLS_OUTPUT_DIR = "all_skills_collection"
TOP_100_COUNT = 100

# JSON 文件路径
ALL_SKILLS_JSON = SCRIPT_DIR / "all_skills.json"
SKILLS_SH_JSON = SCRIPT_DIR / "skills_sh_all.json"

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

def load_all_skills_json() -> List[Dict]:
    """从 all_skills.json 加载本地技能"""
    print_info("加载本地技能数据...")

    if not ALL_SKILLS_JSON.exists():
        print_error(f"all_skills.json 不存在于 {ALL_SKILLS_JSON}")
        print_error("请先运行 scan_skills.py")
        return []

    with open(ALL_SKILLS_JSON, 'r', encoding='utf-8') as f:
        skills = json.load(f)

    print_success(f"加载了 {len(skills)} 个本地技能")
    return skills

def load_top_skills_sh(count: int = TOP_100_COUNT) -> List[Dict]:
    """从 skills_sh_all.json 加载前 N 个技能"""
    print_info(f"加载 skills.sh 前 {count} 个技能...")

    if not SKILLS_SH_JSON.exists():
        print_warning(f"skills_sh_all.json 不存在于 {SKILLS_SH_JSON}，跳过 skills.sh 技能")
        return []

    with open(SKILLS_SH_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
        skills = data.get('skills', [])[:count]

    print_success(f"加载了 {len(skills)} 个 skills.sh 技能")
    return skills

def categorize_skills(skills: List[Dict]) -> Dict[str, List[Dict]]:
    """按源对技能进行分类"""
    print_info("分类技能...")

    categorized = {}
    for skill in skills:
        source = skill.get('source', 'unknown')
        if source not in categorized:
            categorized[source] = []
        categorized[source].append(skill)

    for source, source_skills in categorized.items():
        print_success(f"  {source}: {len(source_skills)} 个技能")

    return categorized

def generate_markdown(local_skills: List[Dict], skills_sh_skills: List[Dict]) -> str:
    """生成 Markdown 目录"""

    print_info("生成 Markdown 目录...")

    # 分类本地技能
    local_by_source = {}
    for skill in local_skills:
        source = skill.get('source', 'unknown')
        if source not in local_by_source:
            local_by_source[source] = []
        local_by_source[source].append(skill)

    # 生成 Markdown
    md_content = f"""# 全部技能目录整合

> 生成时间: {subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()}

## 📊 统计概览

| 类别 | 技能数量 |
|------|---------|
| **本地 Submodules 技能** | {len(local_skills):,} |
| **Skills.sh Top {TOP_100_COUNT}** | {len(skills_sh_skills):,} |
| **总计** | {len(local_skills) + len(skills_sh_skills):,} |

---

## 📦 本地 Submodules 技能 ({len(local_skills):,} 个)

这些技能来自项目的 git submodules，存储在 `submodules/` 目录中。

"""

    # 添加本地技能分类
    for source in sorted(local_by_source.keys()):
        skills = local_by_source[source]
        md_content += f"\n### {source.replace('-', ' ').title()} ({len(skills)} 个)\n\n"
        md_content += "| # | 技能名称 | 描述 | 路径 |\n"
        md_content += "|---|---------|------|------|\n"

        for i, skill in enumerate(skills[:50], 1):  # 每个源最多显示 50 个
            name = skill.get('name', 'unknown')
            description = skill.get('description', '')[:60]
            path = skill.get('path', '')

            md_content += f"| {i} | `{name}` | {description} | `{path}` |\n"

        if len(skills) > 50:
            md_content += f"| ... | ... | ... | ... 还有 {len(skills) - 50} 个技能 |\n"

    # 添加 Skills.sh Top 100
    md_content += f"""

---

## 🌟 Skills.sh Top {TOP_100_COUNT} ({len(skills_sh_skills)} 个)

这些是 skills.sh 平台上最受欢迎的技能，按安装量排序。

### 按安装量排序 (Top 20)

| 排名 | 技能名称 | 安装量 | 来源仓库 |
|------|---------|--------|----------|
"""

    # Top 20 详细表格
    for i, skill in enumerate(skills_sh_skills[:20], 1):
        name = skill.get('name', 'unknown')
        installs = skill.get('installs', 0)
        source = skill.get('topSource', 'unknown')

        md_content += f"| {i} | `{name}` | {installs:,} | {source} |\n"

    md_content += "\n### 完整列表 (21-100)\n\n"
    md_content += "| 排名 | 技能名称 | 安装量 | 来源仓库 |\n"
    md_content += "|---|---------|--------|----------|\n"

    # 21-100 简化表格
    for i, skill in enumerate(skills_sh_skills[20:], 21):
        name = skill.get('name', 'unknown')
        installs = skill.get('installs', 0)
        source = skill.get('topSource', 'unknown')

        md_content += f"| {i} | `{name}` | {installs:,} | {source} |\n"

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

*此文件由 `integrate_and_download_skills.py` 自动生成*
"""

    return md_content

def save_markdown(content: str, filename: str = OUTPUT_MD):
    """保存 Markdown 文件"""
    output_path = SCRIPT_DIR / filename
    print_info(f"保存 Markdown 文件到 {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print_success(f"Markdown 文件已保存: {output_path}")

def copy_local_skills(local_skills: List[Dict]):
    """复制本地技能到统一目录"""
    print_header("复制本地技能到统一目录")

    output_dir = SCRIPT_DIR / SKILLS_OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)

    print_info(f"目标目录: {output_dir.absolute()}")

    copied = 0
    skipped = 0

    for skill in local_skills:
        skill_path = skill.get('path', '')

        # 尝试相对于脚本目录的路径
        skill_path_abs = SCRIPT_DIR / skill_path if not os.path.isabs(skill_path) else Path(skill_path)

        if not skill_path or not skill_path_abs.exists():
            skipped += 1
            continue

        # 获取技能目录
        skill_dir = skill_path_abs.parent
        skill_name = skill.get('name', 'unknown')

        # 目标路径
        dest_dir = output_dir / skill_name

        # 如果已存在，跳过
        if dest_dir.exists():
            skipped += 1
            continue

        try:
            # 复制整个目录
            shutil.copytree(skill_dir, dest_dir)
            copied += 1

            if copied % 100 == 0:
                print_success(f"已复制 {copied} 个技能...")

        except Exception as e:
            print_error(f"复制失败 {skill_name}: {e}")
            skipped += 1

    print_success(f"复制完成: {copied} 个成功, {skipped} 个跳过")

def download_skills_sh_skills(skills_sh_skills: List[Dict]):
    """下载 skills.sh 技能到本地"""
    print_header("下载 Skills.sh 技能")

    output_dir = SCRIPT_DIR / SKILLS_OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)

    print_info(f"目标目录: {output_dir.absolute()}")
    print_warning("注意: 这需要网络连接和 npx skills 命令")

    # 询问用户是否继续
    response = input(f"\n是否下载 {len(skills_sh_skills)} 个 skills.sh 技能? (y/N): ").strip().lower()

    if response != 'y':
        print_info("跳过下载 skills.sh 技能")
        return

    downloaded = 0
    failed = 0

    for i, skill in enumerate(skills_sh_skills, 1):
        skill_id = skill.get('id', skill.get('name', 'unknown'))
        skill_name = skill.get('name', 'unknown')
        installs = skill.get('installs', 0)

        print(f"\n[{i}/{len(skills_sh_skills)}] 下载 {skill_name} ({installs:,} 安装)...")

        try:
            # 使用 npx skills add 下载
            # 技能会被下载到 ~/.claude/skills/ 或用户指定的目录
            cmd = ['npx', 'skills', 'add', skill_id]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                downloaded += 1
                print_success(f"✓ 下载成功: {skill_name}")
            else:
                failed += 1
                print_warning(f"✗ 下载失败: {skill_name}")
                if result.stderr:
                    print_error(f"  错误: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            failed += 1
            print_error(f"超时: {skill_name}")
        except Exception as e:
            failed += 1
            print_error(f"异常: {skill_name} - {e}")

        # 每 10 个显示进度
        if i % 10 == 0:
            print_info(f"进度: {i}/{len(skills_sh_skills)}, 成功: {downloaded}, 失败: {failed}")

    print_success(f"\n下载完成: {downloaded} 个成功, {failed} 个失败")

def create_collection_readme():
    """创建集合目录的 README"""
    readme_content = """# 全部技能集合

这个目录包含了从各个来源整合的所有技能。

## 目录结构

- `all_skills_collection/` - 所有技能的统一目录
  - 本地 submodules 技能（复制）
  - skills.sh 技能（下载）

## 使用方法

这些技能可以：
1. 直接被 Claude Code 使用
2. 作为参考和学习的资源
3. 复制到其他项目中

## 更新

运行 `python3 integrate_and_download_skills.py` 来更新此集合。

---
*由 integrate_and_download_skills.py 自动生成*
"""

    readme_path = SCRIPT_DIR / SKILLS_OUTPUT_DIR / "README.md"
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
  %(prog)s                    # 只生成 Markdown 文件（默认）
  %(prog)s --copy             # 生成 MD 并复制本地技能
  %(prog)s --copy --download  # 生成 MD、复制技能并下载 skills.sh 技能
  %(prog)s --download-only    # 只下载 skills.sh 技能
  %(prog)s --top 200          # 包含 skills.sh 前 200 个技能
        """
    )

    parser.add_argument(
        '--copy', '-c',
        action='store_true',
        help='复制本地 submodules 技能到统一目录'
    )

    parser.add_argument(
        '--download', '-d',
        action='store_true',
        help='下载 skills.sh 技能到本地（需要 npx）'
    )

    parser.add_argument(
        '--download-only',
        action='store_true',
        help='只下载 skills.sh 技能，跳过其他操作'
    )

    parser.add_argument(
        '--top', '-n',
        type=int,
        default=TOP_100_COUNT,
        metavar='N',
        help=f'包含 skills.sh 前 N 个技能（默认: {TOP_100_COUNT}）'
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

    # 如果是只下载模式
    if args.download_only:
        if not args.quiet:
            print_info("只下载模式：仅下载 skills.sh 技能")

        skills_sh_skills = load_top_skills_sh(args.top)
        if skills_sh_skills:
            download_skills_sh_skills(skills_sh_skills)
        return

    # 1. 加载本地技能
    local_skills = load_all_skills_json()
    if not local_skills:
        print_error("无法继续，请确保 all_skills.json 存在")
        sys.exit(1)

    # 2. 加载 skills.sh 前 N 个
    skills_sh_skills = load_top_skills_sh(args.top)

    # 3. 生成 Markdown
    md_content = generate_markdown(local_skills, skills_sh_skills)
    save_markdown(md_content, args.output)

    # 4. 复制本地技能（如果指定了 --copy）
    if args.copy:
        copy_local_skills(local_skills)
        create_collection_readme()
    else:
        if not args.quiet:
            print_info("跳过复制技能（使用 --copy 参数来复制）")

    # 5. 下载 skills.sh 技能（如果指定了 --download）
    if args.download and skills_sh_skills:
        download_skills_sh_skills(skills_sh_skills)
    elif skills_sh_skills and not args.quiet:
        print_info("跳过下载 skills.sh 技能（使用 --download 参数来下载）")

    # 完成
    if not args.quiet:
        print_header("✅ 完成")

        print_success(f"✓ Markdown 目录已生成: {args.output}")

        if args.copy:
            print_success(f"✓ 技能已整合到: {SKILLS_OUTPUT_DIR}/")

        print_info(f"\n查看目录: cat {args.output}")
        if args.copy:
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
