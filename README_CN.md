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
git clone <your-repo-url>
cd erduo-skills
```

## 使用方式

### 生成日报

将仓库加载到你的 Agent 环境（例如 Claude Desktop 或支持 MCP 的 IDE），执行 `daily-news-report` 技能。

示例提示词：

```
生成今天的日报。
```

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
