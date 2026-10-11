# 安装 SciWrite

SciWrite 的技能名是 `write-technical-plans`，安装时请复制**整个同名文件夹**。只复制 `SKILL.md` 会丢失写作参考、排版配置和脚本。

本页说明 Codex 的本地技能安装。其他工具是否支持该目录结构、脚本运行和文件交付，请以各工具的文档为准。

## 1. 取得完整文件夹

可以下载正式版本的 [SciWrite.zip](https://github.com/2158076627-gif/SciWrite/releases/latest/download/SciWrite.zip)，解压后进入包含 `write-technical-plans` 的目录；也可以用 Git 克隆仓库：

```bash
git clone https://github.com/2158076627-gif/SciWrite.git
cd SciWrite
```

安装前应能看到以下结构。`agents`、`assets`、`references` 和 `scripts` 都要保留：

```text
write-technical-plans/
├── SKILL.md
├── agents/openai.yaml
├── assets/
├── references/
└── scripts/apply_style.py
```

## 2. 选择安装范围

| 范围 | Windows | macOS / Linux |
| --- | --- | --- |
| 个人全局，供多个项目使用 | `%USERPROFILE%\.agents\skills\write-technical-plans` | `~/.agents/skills/write-technical-plans` |
| 项目内，供该项目使用 | `<项目目录>\.agents\skills\write-technical-plans` | `<项目目录>/.agents/skills/write-technical-plans` |

Codex 会扫描用户技能目录；在 Git 仓库内，也会扫描从当前工作目录到仓库根目录的 `.agents/skills`。同名技能不会合并，因此通常选择一种安装范围即可。目录和发现规则核对于 **2026-10-11**，依据 [OpenAI 官方 Build skills 文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。

### Windows / PowerShell

在步骤 1 的目录运行以下完整代码。目标已存在时会停止，不会覆盖旧版：

```powershell
& {
    $sciwriteSource = (Resolve-Path -LiteralPath '.\write-technical-plans').Path
    $sciwriteSkillsRoot = Join-Path $env:USERPROFILE '.agents\skills'
    $sciwriteTarget = Join-Path $sciwriteSkillsRoot 'write-technical-plans'

    if (-not (Test-Path -LiteralPath (Join-Path $sciwriteSource 'SKILL.md') -PathType Leaf)) {
        throw '来源目录缺少 SKILL.md，请检查解压位置。'
    }
    if (Test-Path -LiteralPath $sciwriteTarget) {
        throw '已安装同名技能。请先按下方更新步骤备份旧版。'
    }
    New-Item -ItemType Directory -Path $sciwriteSkillsRoot -Force | Out-Null
    Copy-Item -LiteralPath $sciwriteSource -Destination $sciwriteTarget -Recurse
    Get-Item -LiteralPath (Join-Path $sciwriteTarget 'SKILL.md')
}
```

若要安装到项目，把上面 `$sciwriteSkillsRoot = ...` 一行替换为以下三行。输入一个已存在的项目目录：

```powershell
$sciwriteProject = (Resolve-Path -LiteralPath (Read-Host '请输入目标项目的完整路径')).Path
if (-not (Test-Path -LiteralPath $sciwriteProject -PathType Container)) { throw '请输入目录路径。' }
$sciwriteSkillsRoot = Join-Path $sciwriteProject '.agents\skills'
```

### macOS / Linux / Bash

在步骤 1 的目录运行以下完整代码：

```bash
(
  set -e
  sciwrite_source="$PWD/write-technical-plans"
  sciwrite_skills_root="$HOME/.agents/skills"
  sciwrite_target="$sciwrite_skills_root/write-technical-plans"

  test -f "$sciwrite_source/SKILL.md" || { printf '%s\n' '来源目录缺少 SKILL.md。' >&2; exit 1; }
  if [ -e "$sciwrite_target" ] || [ -L "$sciwrite_target" ]; then
    printf '%s\n' '已安装同名技能，请先备份旧版。' >&2
    exit 1
  fi
  mkdir -p "$sciwrite_skills_root"
  cp -R "$sciwrite_source" "$sciwrite_target"
  test -f "$sciwrite_target/SKILL.md"
  printf '已安装到 %s\n' "$sciwrite_target"
)
```

若要安装到项目，把 `sciwrite_skills_root=...` 一行替换为以下三行：

```bash
read -r -p '请输入目标项目的完整路径: ' sciwrite_project
test -d "$sciwrite_project" || { printf '%s\n' '项目目录不存在。' >&2; exit 1; }
sciwrite_skills_root="$sciwrite_project/.agents/skills"
```

## 3. 确认加载并调用

在 Codex CLI 或 IDE 扩展中输入 `/skills` 查看技能，或在任务开头使用：

```text
$write-technical-plans
根据我的研究问题和附件，撰写一份研究方案，说明证据、方法、实施步骤和验证条件。
```

显示名称为“科研项目书与计划书撰写”。Codex 会自动发现技能变更；未出现时重启 Codex，再确认 `SKILL.md` 所在路径，尤其避免多套一层目录。调用方式依据 [OpenAI 官方 Build skills 文档](https://learn.chatgpt.com/docs/build-skills#how-chatgpt-and-codex-use-skills)。更多任务提示见 [使用指南](usage.md)。

## 更新已有安装

先将旧版移到技能扫描目录之外，再运行首次安装命令。请勿将备份留在 `.agents/skills` 中，以免它作为另一个同名技能被发现。

全局安装的 PowerShell 备份示例：

```powershell
& {
    $sciwriteSkillsRoot = [IO.Path]::GetFullPath((Join-Path $env:USERPROFILE '.agents\skills'))
    $sciwriteOld = Join-Path $sciwriteSkillsRoot 'write-technical-plans'
    $sciwriteBackupRoot = [IO.Path]::GetFullPath((Join-Path $env:USERPROFILE '.agents\skill-backups'))
    $sciwriteBackup = Join-Path $sciwriteBackupRoot ('write-technical-plans-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    if (-not (Test-Path -LiteralPath $sciwriteOld -PathType Container)) {
        throw '未找到旧版，请确认安装范围。'
    }
    Write-Output "旧版：$sciwriteOld"
    Write-Output "备份：$sciwriteBackup"
    New-Item -ItemType Directory -Path $sciwriteBackupRoot -Force | Out-Null
    Move-Item -LiteralPath $sciwriteOld -Destination $sciwriteBackup
}
```

全局安装的 Bash 备份示例：

```bash
(
  set -e
  sciwrite_old="$HOME/.agents/skills/write-technical-plans"
  sciwrite_backup_root="$HOME/.agents/skill-backups"
  sciwrite_backup="$sciwrite_backup_root/write-technical-plans-$(date +%Y%m%d-%H%M%S)-$$"
  test -d "$sciwrite_old" || { printf '%s\n' '未找到旧版。' >&2; exit 1; }
  mkdir -p "$sciwrite_backup_root"
  test ! -e "$sciwrite_backup"
  mv "$sciwrite_old" "$sciwrite_backup"
  printf '旧版已备份到 %s\n' "$sciwrite_backup"
)
```

项目安装时，将示例中的旧版路径换成该项目 `.agents/skills/write-technical-plans` 的完整路径；备份仍放在用户目录的 `.agents/skill-backups`。更新后试用一次，确认结果符合预期再决定是否清理备份。

## Word 排版脚本的依赖

读取写作参考、起草文字不要求安装 Python。运行 `apply_style.py` 需要 **Python 3.9+ 和 `lxml`**；仅在用 Python 创建 Word 文档时，另装 `python-docx`。依赖来自 [脚本](../write-technical-plans/scripts/apply_style.py) 和 [独立运行说明](../write-technical-plans/references/portable-docx.md)。

以下命令在全局安装后执行。Windows 若使用 Python Launcher，可将 `python` 换成 `py`：

```powershell
python -m pip install lxml
python "$env:USERPROFILE\.agents\skills\write-technical-plans\scripts\apply_style.py" draft.docx --output final.docx
```

```bash
python3 -m pip install lxml
python3 "$HOME/.agents/skills/write-technical-plans/scripts/apply_style.py" draft.docx --output final.docx
```

如需用 Python 新建 `.docx`，再运行 `python -m pip install python-docx`，或对应的 `python3` 命令。项目安装时调整脚本路径。

脚本统一格式；文献检索、取得原图和逐页检查依赖使用环境提供的工具。本包不附字体。完整制作与验收步骤见 [独立运行与 Word 检查](../write-technical-plans/references/portable-docx.md)。

[返回首页](../README.md) · [使用指南](usage.md)
