# 独立运行与 Word 检查

本技能的写作参考和排版配置可以独立使用。若环境提供 documents 技能，优先遵循其制作、渲染与视觉检查流程；本文件用于该技能不可用时的替代步骤。参考样稿不是运行必需文件。

## 环境与依赖

统一排版脚本需要 Python 3.9 或更新版本及 `lxml`；用代码新建 Word 时另需 `python-docx`。使用当前环境指定的 Python，普通本地环境可运行：

```bash
python -m pip install lxml python-docx
python "<本技能目录>/scripts/apply_style.py" --help
```

离线环境没有相应依赖时，先完成正文及图表规划，明确尚未生成或检查的文件，不能把 Markdown 改扩展名冒充 Word。排版配置要求宋体、黑体与 Times New Roman；本包不附字体。渲染机缺少字体时安装合法可用的相应字体或按用户要求采用替代字体，并说明可能发生的版式差异。

## 制作与统一排版

使用 `python-docx` 或可保留 OOXML 的编辑工具创建 `.docx`。设置 Title、Subtitle、Heading 1–3、Normal 等语义样式；创建 PlanMetadata、PlanReference、PlanTableCaption、PlanFigureCaption，其中两种题注样式继承 Caption。图题置下、表题置上，图像保持长宽比，表格列宽与页内可用宽度匹配。

新增表格按 `tables-and-charts.md` 标记 `three_line` 和实际表头行数。纯图片布局才使用 `plain`。未标记的内容表格仍会按默认配置转为三线表，需检查原表的底色是否承载尚未文字化的信息。

```bash
python "<本技能目录>/scripts/apply_style.py" draft.docx --output final.docx
```

脚本仅修改格式，不负责写作、自动检索或取得论文图片，不决定表格列宽和图像分页。调用工具生成正文和插图后，再运行脚本。修改既有文档前保留原件，输出为新文件；仅应用格式时检查正文、字段、图片与链接未变。

## 渲染与验收

可以在 Microsoft Word 导出 PDF 并逐页检查，或在已安装 LibreOffice 和 Poppler 的环境运行：

```bash
libreoffice -env:UserInstallation=file:///tmp/research-plan-lo --headless --convert-to pdf --outdir preview final.docx
pdftoppm -png -r 120 preview/final.pdf preview/page
```

上述临时目录示例用于 Linux/macOS；Windows 可在 Word 或 LibreOffice 图形界面导出 PDF。先创建 `preview` 目录。多任务渲染时为 LibreOffice 使用各自临时配置目录。

逐页核对中文与英文是否正常显示、正文两字符缩进、标题层级、白底黑字三线表、跨页表头、图与题注相邻，以及图片和单位的可读性。检查裁切、重叠、孤立标题、异常空白和不可点击来源；检查正文确实引用并解释相邻插图。修正后重新导出受影响内容，直至通过视觉检查。

无法渲染或查看页面时，至少验证 `.docx` 可打开、压缩包结构完整、所有图表与引用存在，并明确视觉验收尚未完成。不得仅凭脚本退出成功宣称版式无误。

## 保存与交付

按使用环境要求保存用户需要的最终文件。项目书通常交付可编辑 `.docx`，用户要求时另附 PDF；纯综述文字或路线源图按请求交付。预览页、临时脚本和内部检查记录默认不作为成稿交付。
