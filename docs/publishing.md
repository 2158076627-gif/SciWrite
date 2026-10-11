# 发布后的维护与展示

此页供仓库所有者在首次发布后维护 SciWrite。README、展示图和安装包可以分别更新；是否创建正式 Release、选用许可证或启用 Pages，由所有者决定。

## 更新 README 与展示图

README 负责让访客快速理解用途、看到文稿样式并找到安装入口。更新时优先保留这条阅读顺序：用途 → 展示 → 安装 → 示例提示 → 文件与使用边界。

添加展示内容时，将图片放在 `docs/assets/`，使用短而清楚的文件名，在 README 或相关文档中用相对路径引用：

```markdown
![三线表和正文排版示例](docs/assets/你的图片文件名.png)
```

图注说明它展示的能力以及内容性质，例如“结构与排版示例，数据为说明用”。展示图应来自可公开的材料；不要将规划图写成实测结果，也不要将合成展示写成对照实验。修改后在 GitHub 的 Preview 中检查图片、中文、表格和链接。

### 用 Git 更新

在本地仓库修改相关文件，检查差异后提交。以下命令适用于 PowerShell 和 Bash；推送到当前分支，若分支保护要求 PR，则通过 PR 合并：

```bash
git pull --ff-only
git status --short
git diff -- README.md docs
git add -- README.md docs
git diff --cached --stat
git diff --cached
git commit -m "docs: update SciWrite showcase"
git push
```

只改了部分文件时，将 `git add` 的路径缩小到对应文件。若工作区已有未提交修改，先完成或保存本地工作，再执行 `git pull`。技能规则、排版配置和安装包的变更应另行核对并在提交说明中写清楚。

### 用 GitHub 网页更新

打开要修改的 Markdown 文件，点击编辑按钮，完成后切换到 Preview 检查。通过 Commit changes 提交，或创建分支并提交 PR。上传新图片可使用仓库的 Add file → Upload files；图片提交后，再更新 Markdown 中的相对路径。

## 完善 About 与个人主页

在仓库首页 About 旁的齿轮中编辑描述和 Topics。可采用以下描述：

> 面向中文科研项目书、研究方案、论文综述与技术路线的 Codex 技能：证据论证、自然学术表达、三线表与 Word 排版。

Topics 建议从实际用途选取：

```text
codex
agent-skills
scientific-writing
research-proposal
literature-review
technical-writing
chinese
docx
```

Topics 使用小写字母、数字和连字符；操作入口见 [GitHub 官方 Topics 指南](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)。

若希望访客在个人主页先看到项目，打开个人主页 → Customize your pins，选中 SciWrite 后保存。仓库和 Gist 合计最多置顶六项，依据 [GitHub 官方置顶指南](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile)。

## 设置分享预览图

分享预览图与 README 内图片分别设置。在仓库 Settings → Social preview → Edit → Upload an image 上传图片。GitHub 建议采用 1280 × 640 像素、低于 1 MB 的 PNG、JPG 或 GIF，见 [官方预览图指南](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)。

图片可简洁呈现 SciWrite 名称、中文科研写作用途和一个文稿片段。检查小尺寸下的可读性，避免大量小字；封面中的主张应与 README 和技能实际能力一致。

## 可选：创建版本 Release

仓库已有可下载的 [SciWrite.zip](../SciWrite.zip)。若希望用户固定下载某个版本，可为经过核对的提交创建 Release，并将这个分发 ZIP 作为附件上传。Release 的版本号、稳定性标记和发布时间由所有者决定；下面的 `v1.0.0` 仅是版本名示例。

发布前先确认 ZIP 中的 `write-technical-plans` 与目标提交的技能文件一致，解压后目录完整，不含个人项目原稿或临时输出。技能有改动时，先更新并检查分发包；不要让 Release 说明与旧 ZIP 混用。

1. 在仓库的 Releases 中点击 Draft a new release。
2. 选择已有 tag，或创建一个版本 tag（例如 `v1.0.0`），并选择包含本次版本的目标提交或分支。
3. 填写标题与说明，写清楚新增能力、修订规则、兼容要求和已完成的检查。
4. 在附件区域上传 `SciWrite.zip`。根据版本状态选择是否标记为 pre-release。
5. 先保存草稿并核对附件；准备好后点击 Publish release。

创建和附件操作依据 [GitHub 官方 Release 指南](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)。创建 Release 不会替代仓库中的源码维护；新的版本应对应新的可追溯 tag。

说明可采用以下格式，并填入本次实际信息：

```markdown
SciWrite v1.0.0

- 内容：中文科研计划、研究方案、综述与技术路线的写作参考、排版配置和脚本。
- 安装：解压附件，完整复制 write-technical-plans 文件夹；见 docs/installation.md。
- 依赖：仅 Word 排版脚本需要 Python 3.9+ 与 lxml；用 Python 新建 Word 另需 python-docx。
- 本次变化：[填写实际变化]
- 已完成检查：[填写实际执行的检查，不将展示样例写成性能测试]
- 已知限制：[填写尚未核验的兼容性或工具条件]
```

首次 Release 发布并设为 latest 后，可以把 README 的下载入口改为其正式附件链接。固定版本链接用于可复现下载；`releases/latest/download/SciWrite.zip` 用于最新版本。链接规则见 [GitHub 官方 Release 链接指南](https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases)。在 Release 实际存在之前，继续使用仓库 ZIP 链接。

## 许可证与 Pages

公开仓库与授权条款是两件事。所有者选定许可证后，再添加相应 `LICENSE` 并同步 README、贡献说明和后续 Release；此前不要展示未经确认的许可证徽章或宣称已按某许可证开放。技能中的参考资料、后续使用的论文图和设备图，仍应按各自来源核对使用条件。

GitHub Pages 可以作为后续独立展示页。当前 README 已可承载介绍、图库和安装入口；需要网页导航或单独展示站点时，再决定 Pages 的内容与部署来源。本指南不预设 Pages 已启用。

GitHub 界面与链接核对日期：**2026-10-11**。界面变化时按以上官方文档更新操作说明。

[返回首页](../README.md) · [安装指南](installation.md) · [使用指南](usage.md)
