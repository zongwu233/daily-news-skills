# Daily News Skills / 每日日报技能库

[English](README.md)

本工程基于 https://github.com/rookie-ricardo/erduo-skills 。

Daily News Skills 是一个面向 AI Agent 的技能仓库，专注于生成高质量的每日日报，并提供本地网页阅读体验。

## 功能

- 多源抓取与摘要生成
- 结构化 Markdown 报告（`NewsReport/`）
- 本地 Astro 阅读网站
- Light/Dark 模式切换，提升阅读舒适度

## 项目结构

```bash
├── .claude/
│   └── agents/            # Agent 定义
├── skills/
│   └── daily-news-report/ # 每日日报技能
├── NewsReport/            # 生成的 Markdown 日报
├── news-report-website/   # Astro 日报网站
├── README.md              # English 文档
└── README_CN.md           # 中文文档
```

## 环境要求

- Node.js >= 18.20.8
- npm >= 9

## 安装

```bash
git clone git@github.com:zongwu233/daily-news-skills.git
cd daily-news-skills
```

## 使用方式

### 生成每日日报

本仓库提供 `daily-news-report` 技能，可自动从多个信息源（Hacker News、Hugging Face Papers、Paul Graham 文章等）聚合内容并生成结构化的 Markdown 报告。

#### 生成日报的步骤：

1. **加载仓库**到你的 AI Agent 环境（Claude Desktop、Cursor、Windsurf 或任何支持 MCP 的 IDE）
2. **调用技能**，使用简单的提示词：
   ```
   生成今天的日报。
   ```
   或指定日期：
   ```
   生成 2026-02-15 的日报。
   ```
3. **等待完成** - Agent 会：
   - 从 Tier1 源抓取内容（Hacker News、Hugging Face Papers、Paul Graham、Dmitry Brant）
   - 评估质量和数量（目标：50 条高质量内容）
   - 如有需要，从额外源抓取
   - 去重和筛选内容
   - 在 `NewsReport/` 目录生成 Markdown 报告
   - 更新缓存统计
4. **查找输出** - 报告保存为 `NewsReport/YYYY-MM-DD-news-report.md`

#### 报告结构：

每份报告包含：
- 50 条高质量新闻条目及摘要
- 质量评分（1-5 星）
- 来源标注和关键词
- 统计信息头（使用的源、收录条目数、生成时间）

#### 提示：

- 技能会在从 Tier1 源收集到 50 条高质量内容后自动停止
- 如果源内容不足，会从 Tier2/Tier3 源继续抓取
- 内容会缓存以避免跨日重复
- 失败的源会被记录但不会阻塞流程

### 启动阅读网站

```bash
cd news-report-website
npm install
npm run dev
```

访问：

```
http://localhost:4321/news-report
```

## 贡献

欢迎贡献。请参考 `skills/` 下的已有结构扩展新的技能。

---

Created with ❤️ by Daily News Skills Team
