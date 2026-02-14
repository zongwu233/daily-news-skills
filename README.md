# Daily News Skills

[中文](README_CN.md)

This project is based on https://github.com/rookie-ricardo/erduo-skills.

Daily News Skills is a collection of AI agent skills focused on generating high-quality daily news reports and rendering them in a local web reader.

## Features

- Multi-source news aggregation and summarization
- Structured Markdown reports in `NewsReport/`
- Local Astro website for reading reports in a browser
- Light/Dark mode toggle for comfortable reading

## Project Structure

```bash
├── .claude/
│   └── agents/            # Agent personas & prompts
├── skills/
│   └── daily-news-report/ # Daily news report skill
├── NewsReport/            # Generated Markdown reports
├── news-report-website/   # Astro web reader
├── README.md              # English documentation
└── README_CN.md           # 中文文档
```

## Requirements

- Node.js >= 18.20.8
- npm >= 9

## Install

```bash
git clone git@github.com:zongwu233/daily-news-skills.git
cd daily-news-skills
```

## Usage

### Generate Daily News Reports

This repository provides a `daily-news-report` skill that automatically aggregates content from multiple sources (Hacker News, Hugging Face Papers, Paul Graham essays, etc.) and generates structured Markdown reports.

#### Steps to generate a report:

1. **Load the repository** into your AI agent environment (Claude Desktop, Cursor, Windsurf, or any MCP-enabled IDE)
2. **Invoke the skill** by using a simple prompt:
   ```
   Generate today's news report.
   ```
   Or specify a date:
   ```
   Generate daily news report for 2026-02-15.
   ```
3. **Wait for completion** - the agent will:
   - Fetch content from Tier1 sources (Hacker News, Hugging Face Papers, Paul Graham, Dmitry Brant)
   - Evaluate quality and quantity (target: 50 high-quality items)
   - Fetch from additional sources if needed
   - Deduplicate and filter content
   - Generate a Markdown report in `NewsReport/` directory
   - Update cache statistics
4. **Locate the output** - reports are saved as `NewsReport/YYYY-MM-DD-news-report.md`

#### Report structure:

Each report contains:
- 50 high-quality news items with summaries
- Quality ratings (1-5 stars)
- Source attribution and keywords
- Statistics header (sources used, items collected, generation time)

#### Tips:

- The skill automatically stops when it has collected 50 high-quality items from Tier1 sources
- If sources are insufficient, it will fetch from Tier2/Tier3 sources
- Content is cached to avoid duplicates across days
- Failed sources are logged but don't block the process

### Run the web reader

```bash
cd news-report-website
npm install
npm run dev
```

Open:

```
http://localhost:4321/news-report
```

## Contributing

Contributions are welcome. Please check the `skills/` folder for patterns and extend existing skills.

---

Created with ❤️ by Daily News Skills Team
