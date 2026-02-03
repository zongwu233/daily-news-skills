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
git clone <your-repo-url>
cd erduo-skills
```

## Usage

### Generate reports

Load this repository into your agent environment (Claude Desktop or any MCP-enabled IDE) and run the daily news report skill.

Example prompt:

```
Generate today's news report.
```

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
