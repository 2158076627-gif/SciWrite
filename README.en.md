<div align="center">

<img src="docs/assets/hero.png" alt="SciWrite — research writing from evidence to an editable document" width="100%">

**A reusable AI skill for Chinese research plans, proposals, literature reviews, and technical roadmaps.**

<p>
  <img src="https://img.shields.io/badge/Skill-write--technical--plans-0F766E?style=flat-square" alt="Skill: write-technical-plans">
  <img src="https://img.shields.io/badge/Output-Editable_Word-2563EB?style=flat-square" alt="Output: editable Word">
  <img src="https://img.shields.io/badge/Writing-Evidence_led-7C3AED?style=flat-square" alt="Writing: evidence led">
</p>

[简体中文](README.md) · **English**

[Examples](#examples) · [Quick start](#quick-start) · [Workflow](#workflow) · [Word formatting](#word-formatting) · [Repository](#repository) · [Scope and reuse](#scope-and-reuse)

</div>

SciWrite connects a research question to its evidence, chosen methods, resources, implementation steps, and validation conditions. It helps draft and revise specific, coherent academic prose, then applies a configurable Word style with three-line tables. The reusable skill is named **`write-technical-plans`**; SciWrite is its public showcase.

## Examples

Explore actual document previews and download the editable files. The two examples show a 37-page robot assembly research plan and a 17-page progress report. Page counts refer to the exported PDFs.

<table>
  <tr>
    <th width="50%">Research plan</th>
    <th width="50%">Progress report</th>
  </tr>
  <tr>
    <td align="center"><a href="examples/research-plan/Robot_Assembly_Research_Plan.pdf"><img src="docs/assets/previews/research-plan.png" alt="Preview pages from the robot assembly research plan" width="420"></a></td>
    <td align="center"><a href="examples/progress-report/Robot-Assembly-Progress-Report.pdf"><img src="docs/assets/previews/progress-report.png" alt="Preview pages from the robot assembly progress report" width="420"></a></td>
  </tr>
  <tr>
    <td align="center"><a href="examples/research-plan/Robot_Assembly_Research_Plan.docx">Editable Word</a> · <a href="examples/research-plan/Robot_Assembly_Research_Plan.pdf">Read PDF</a></td>
    <td align="center"><a href="examples/progress-report/Robot-Assembly-Progress-Report.docx">Editable Word</a> · <a href="examples/progress-report/Robot-Assembly-Progress-Report.pdf">Read PDF</a></td>
  </tr>
</table>

These are illustrative research documents, with their original research content retained. Their research claims, references, and reported or planned results have not been independently verified for this repository. Use them to inspect structure and layout; verify any scientific content before relying on it.

## What the skill helps you do

| Task | Writing focus |
|---|---|
| Research project plans and proposals | Define the problem, compare routes, connect methods and resources, and specify stage outputs and acceptance conditions. |
| Research designs | Explain assumptions, method choices, experiments or implementation, fair controls, and adjustment conditions. |
| Literature reviews and research background | Organize sources by questions or mechanisms, compare methods and evidence boundaries, and identify research gaps. |
| Technical roadmaps | Connect each module's inputs, outputs, dependencies, and validation to the written argument. |
| Draft revision | Preserve useful ideas and terminology, strengthen reasoning, and remove repetition and generic prose. |
| Word formatting | Apply semantic styles, consistent fonts and indentation, captions, and white-background three-line tables. |

Chapters and length follow the needs of the project. The skill does not prescribe a fixed chapter count or page count. It asks authors to distinguish existing facts, sourced facts, proposals, planning values, and testable assumptions.

## Quick start

**1. Get the skill.** Download [SciWrite.zip](SciWrite.zip), or use the [`write-technical-plans/`](write-technical-plans/) directory in this repository. Copy the complete skill directory with its name and internal structure intact.

**2. Install it.** Choose a personal or project skill directory:

| Installation | Expected location of `SKILL.md` |
|---|---|
| macOS / Linux, personal | `~/.agents/skills/write-technical-plans/SKILL.md` |
| Windows, personal | `%USERPROFILE%\.agents\skills\write-technical-plans\SKILL.md` |
| Project | `<project>/.agents/skills/write-technical-plans/SKILL.md` |

**3. Invoke it.** Find it with `/skills` in Codex or include `$write-technical-plans` in your prompt. Restart the client if it does not appear. Back up an existing installation before replacing it. See the [installation guide](docs/installation.md) for details and client-specific notes.

Provide your research question, available resources, intended readers, desired length, existing draft, and source materials when available. For example:

```text
$write-technical-plans
Draft a Chinese research project plan for [topic] using the attached materials.
Explain the research problem, route selection, implementation steps, stage
deliverables, and validation conditions. Distinguish evidence from assumptions,
use three-line tables, and produce an editable Word document.
```

```text
$write-technical-plans
Revise the attached Chinese research design. Preserve my useful ideas and
technical terms, strengthen the problem–method–validation relationship,
and remove repetitive prose. Verify citations and explain the relevance
and limits of any literature figures beside the corresponding discussion.
```

More prompts for reviews, roadmaps, and formatting are in the [usage guide](docs/usage.md).

## Workflow

<p align="center"><img src="docs/assets/workflow.png" alt="Research inputs, evidence checks, argument and validation design, Word formatting, and page-by-page review" width="100%"></p>

1. **Frame the problem.** Check assumptions, missing information, available conditions, and the boundaries of the chosen route.
2. **Build the argument.** Connect evidence to method choices, implementation, resources, and fair validation. Give each stage an action, output, and entry condition.
3. **Verify sources and figures.** Check primary sources, publication or equipment versions, figure identities, and reuse conditions. Place relevant figures near the claims they support and explain them in the text.
4. **Apply the Word style.** Use semantic paragraph styles and run the bundled formatting script after drafting.
5. **Review the rendered pages.** Inspect every page for readable text, tables, repeated headers, figures and captions, clipping, awkward breaks, and unsupported claims.

For important research modules, the skill prioritizes **2–3 complementary, relevant, verifiable original figures** from suitable journal sources; exact-model official equipment documentation can support equipment and interface discussions. This is a planning target, not a quota for every section. Relevance, traceability, readability, and valid reuse conditions take precedence. Missing figures are disclosed while the rest of the document proceeds.

## Word formatting

The defaults are defined in [`assets/style.json`](write-technical-plans/assets/style.json): SimSun Chinese body text at 12 pt, SimHei Chinese headings, Times New Roman for Latin text and digits, black text, 1.35 body line spacing, and a two-character first-line indent. Content tables use a white background with top, header, and bottom rules, without vertical rules or cell grids.

Text-only use requires no Python dependencies. The formatting script requires **Python 3.9+ and `lxml`**. Install `python-docx` as well if you create Word documents programmatically:

```bash
python -m pip install lxml
# Optional: for creating DOCX files with Python
python -m pip install python-docx

python write-technical-plans/scripts/apply_style.py draft.docx --output final.docx
```

For a one-off style change, copy the JSON profile into your working directory and edit that copy:

```bash
python write-technical-plans/scripts/apply_style.py draft.docx \
  --output final.docx --profile temporary-style.json
```

The commands above use shell line continuation. In PowerShell, run the `apply_style.py` command on one line. Windows installations may use `py` instead of `python`.

The script applies formatting while retaining document content, fields, links, images, merged cells, column widths, and numbering. It does not write the manuscript, search literature, obtain figures, or decide table widths and page breaks. Inspect the rendered output after formatting. Follow the environment's document workflow when available, or the [standalone Word guide](write-technical-plans/references/portable-docx.md).

Fonts and rendering tools are not bundled. The default fonts need to be available on the rendering machine; substitutions can change layout. A successful script run alone does not establish that the page layout is correct.

## Repository

```text
SciWrite/
├── README.md / README.en.md       Chinese and English showcase
├── SciWrite.zip                   Original distributable skill package
├── write-technical-plans/
│   ├── SKILL.md                   Triggers, workflow, and delivery checks
│   ├── agents/openai.yaml         Display metadata and default prompt
│   ├── assets/style.json          Numeric formatting configuration
│   ├── assets/icon.svg            Skill icon
│   ├── references/                Writing, reviews, figures, tables, Word checks
│   └── scripts/apply_style.py     Content-preserving DOCX formatting
├── examples/                      Editable examples and PDF companions
└── docs/                          Guides and authentic document previews
```

Change [`style.json`](write-technical-plans/assets/style.json) for lasting formatting preferences. Use [`writing-patterns.md`](write-technical-plans/references/writing-patterns.md) for paragraph and argument conventions, [`review-and-routes.md`](write-technical-plans/references/review-and-routes.md) for review and roadmap structure, and [`literature-figures.md`](write-technical-plans/references/literature-figures.md) for figure verification and interpretation. Keep related instructions consistent when customizing the skill.

The original ZIP is retained as the distributable package. The repository separately adds this showcase, guides, and example documents. See the [original user guide](docs/original-user-guide.md) and [publishing guide](docs/publishing.md).

## Scope and reuse

- **Author review remains essential.** Research decisions, citations, source currency, and final claims require verification. The skill promises no research performance, publication outcome, or AI-detection score.
- **Tool availability affects completion.** Browsing, source access, document creation, and rendering depend on the host environment. Unverified sources or unreviewed pages must be identified.
- **Figures retain their original conditions.** Check the applicable license, figure-specific credit lines, third-party exceptions, and permission requirements. Public availability and a citation alone do not establish permission to reproduce a figure. Keep original figure content intact and distinguish literature results from project hypotheses or measurements.
- **The package contains reusable guidance.** It includes no personal project draft, journal figure collection, or font files. The public examples are separate from the installation package.
- **No project license has been selected.** This repository does not yet grant a general reuse license; third-party content remains subject to its own terms. Consult the [publishing guide](docs/publishing.md) before redistribution or public release.
