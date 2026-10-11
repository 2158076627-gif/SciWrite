# 参与改进 SciWrite

欢迎报告安装问题、写作规则冲突、排版异常，或改进说明和示例。请让每项反馈可以被复现和核对。

## 提交 Issue

先搜索已有 Issue。报告问题时尽量提供：

- 使用的客户端、操作系统和技能版本或提交号。
- 全局或项目安装方式，以及实际的 `SKILL.md` 路径。
- 最小任务提示、预期结果和实际结果。
- 脚本问题附 Python 版本、执行命令与完整错误信息。
- 排版问题附已脱敏的小文档或页面截图，并说明字体与渲染工具。

写作建议请给出具体原句、修改方向和理由。事实、引文或配图问题请附原来源、图号或页码；个人材料可替换成最小示例，不必上传完整项目书。

## 提交 Pull Request

Fork 仓库并创建分支，每个 PR 尽量围绕一个问题。PR 描述写清楚问题、修改后的行为和实际执行的检查。

| 修改内容 | 主要位置 |
| --- | --- |
| 触发范围与工作流程 | `write-technical-plans/SKILL.md` |
| 字体、字号、行距、缩进、表线 | `write-technical-plans/assets/style.json` |
| 段落与论证方式 | `write-technical-plans/references/writing-patterns.md` |
| 综述与技术路线 | `write-technical-plans/references/review-and-routes.md` |
| 原图核验与解读 | `write-technical-plans/references/literature-figures.md` |
| 三线表、图表选择与独立运行 | `write-technical-plans/references/` 中的对应文档 |
| Word 格式处理 | `write-technical-plans/scripts/apply_style.py` |
| 安装与公开展示 | `README.md`、`docs/`、`examples/` |

规则或默认值变化时，同步检查关联参考文档、`agents/openai.yaml` 与使用说明，清理相互冲突的旧表述。不要把个人课题的设备、预算或结果变成通用默认值。

## 与改动匹配的检查

- 文档修改：检查相对链接、图片、Markdown 预览和复制命令。
- 写作规则修改：用一个简短的跨主题任务核对新规则与原有流程是否一致，记录观察结果。
- 排版脚本或配置修改：用包含中英文、内容表格、图片与引用的小 `.docx` 验证，处理前后比对文本，并渲染逐页检查。
- 新增展示材料：说明来源与内容性质；示例不作为性能基准或实测效果证明。

未执行的检查写明原因。不要仅凭脚本退出成功宣称版式通过验收，也不要宣称减少套话等同于取得某个 AI 检测分数。

分发 ZIP、版本 Release 和许可证由仓库维护者统一决定与更新。不要在 PR 中增加未经确认的许可证徽章或第三方全文、字体、论文原图及个人项目材料。

[返回首页](README.md) · [使用指南](docs/usage.md)
