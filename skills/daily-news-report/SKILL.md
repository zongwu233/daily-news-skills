---
name: daily-news-report
description: 基于预设 URL 列表抓取内容，筛选高质量技术信息并生成每日 Markdown 报告。
argument-hint: [可选: 日期]
disable-model-invocation: false
user-invocable: true
allowed-tools: Task, WebFetch, Read, Write, Bash(mkdir*), Bash(date*), Bash(ls*), mcp__chrome-devtools__*
---

# Daily News Report v3.0

> **架构升级**：主 Agent 调度 + SubAgent 执行 + 浏览器抓取 + 智能缓存

## 核心架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        主 Agent (Orchestrator)                       │
│  职责：调度、监控、评估、决策、汇总                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│   │ 1. 初始化 │ → │ 2. 调度   │ → │ 3. 监控   │ → │ 4. 评估   │     │
│   │ 读取配置  │    │ 分发任务  │    │ 收集结果  │    │ 筛选排序  │     │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│         │               │               │               │           │
│         ▼               ▼               ▼               ▼           │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│   │ 5. 决策   │ ← │ 够20条？  │    │ 6. 生成   │ → │ 7. 更新   │     │
│   │ 继续/停止 │    │ Y/N      │    │ 日报文件  │    │ 缓存统计  │     │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
         ↓ 调度                              ↑ 返回结果
┌─────────────────────────────────────────────────────────────────────┐
│                        SubAgent 执行层                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │
│   │ Worker A    │   │ Worker B    │   │ Browser     │              │
│   │ (WebFetch)  │   │ (WebFetch)  │   │ (Headless)  │              │
│   │ Tier1 Batch │   │ Tier2 Batch │   │ JS渲染页面   │              │
│   └─────────────┘   └─────────────┘   └─────────────┘              │
│         ↓                 ↓                 ↓                        │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    结构化结果返回                             │   │
│   │  { status, data: [...], errors: [...], metadata: {...} }    │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 配置文件

本 Skill 使用以下配置文件：

| 文件 | 用途 |
|------|------|
| `sources.json` | 信息源配置、优先级、抓取方法 |
| `cache.json` | 缓存数据、历史统计、去重指纹 |

## 执行流程详解

### Phase 1: 初始化

```yaml
步票:
  1. 确定日期（用户参数或当前日期）
  2. 读取 sources.json 获取源配置
  3. 读取新缓存系统获取历史数据
     - 读取 cache/index.json 查看可用日期
     - 如果今日日志不存在，创建新的缓存条目
     - 读取 cache/logs/YYYY-MM-DD.json 获取今日数据
  4. 创建输出目录 NewsReport/
  5. 检查今日是否已有部分报告（追加模式）
```

#### 新缓存系统结构

```
cache/
├── index.json              # 元数据索引（最后更新、可用日期、汇总统计）
├── logs/                   # 每日独立日志
│   ├── 2026-02-02.json  # 完整的每日运行数据
│   └── 2026-02-03.json
├── url_cache/              # URL去重缓存（按月组织）
└── content_hashes/         # 内容指纹（用于跨日去重）
```

#### 缓存读取逻辑

```javascript
// 1. 读取索引
const indexData = await readCacheIndex();
const today = getCurrentDate();

// 2. 检查今日是否已运行
if (indexData.available_dates.includes(today)) {
  // 读取今日日志
  const todayLog = await readDailyLog(today);
  
  // 检查状态（可追加）
  if (todayLog.run_info.phase === 'generating' || todayLog.run_info.phase === 'processing') {
    return { mode: 'append', data: todayLog };
  }
  
  // 已完成，重新运行
  return { mode: 'fresh', data: null };
}

// 3. 创建新的今日日志
return { mode: 'new', data: createNewDailyLog(today) };
```

#### 缓存写入逻辑

```javascript
// 1. 初始化或追加今日日志
const { mode, data } = initializeCache();
let todayLog = mode === 'append' ? data : data;

// 2. 更新每个源的结果
todayLog = await updateSourceResults(todayLog, sourceId, results);

// 3. 更新汇总
todayLog.summary.items_collected = calculateTotalItems(todayLog.sources);
todayLog.summary.items_published = todayLog.articles.length;
todayLog.summary.quality_avg = calculateAverageQuality(todayLog.sources);

// 4. 保存今日日志
await writeDailyLog(today, todayLog);

// 5. 更新索引
await updateCacheIndex(today, todayLog.summary);

// 6. 写入markdown报告
await writeMarkdownReport(todayLog, todayDate);
```

#### 缓存管理函数

```javascript
function createNewDailyLog(date) {
  return {
    schema_version: "2.0",
    description: "Daily News Report 每日运行日志",
    
    run_info: {
      date: date,
      run_id: `run_${date}_001`,
      timestamp: new Date().toISOString(),
      duration_seconds: 0,
      phase: "initializing"
    },
    
    summary: {
      sources_fetched: 0,
      items_collected: 0,
      items_published: 0,
      items_deduped: 0,
      quality_avg: 0.0,
      status: "pending"
    },
    
    sources: initializeSources(),
    url_cache: { urls: [] },
    content_hashes: { hashes: {} },
    articles: { items: [] },
    errors: { items: [] },
    metadata: {
      environment: "local",
      agent_version: "3.0",
      worker_count: 0,
      parallel_enabled: false
    }
  };
}

function initializeSources() {
  return {
    "hn": { "status": "pending", "items_collected": 0 },
    "hf_papers": { "status": "pending", "items_collected": 0 },
    "producthunt": { "status": "pending", "items_collected": 0 },
    "hackernoon_pm": { "status": "pending", "items_collected": 0 },
    "jamesclear": { "status": "pending", "items_collected": 0 },
    "fs_blog": { "status": "pending", "items_collected": 0 },
    "scottyoung": { "status": "pending", "items_collected": 0 },
    "stripe_blog": { "status": "pending", "items_collected": 0 },
    "paulgraham": { "status": "pending", "items_collected": 0 },
    "dmitrybrant": { "status": "pending", "items_collected": 0 }
  };
}
```

### Phase 2: 调度 SubAgent（并行执行）

**策略**：使用 `background_task` 并行调用多个 explore agent，实时监控进度，动态调整批次

```yaml
第1波 (并行启动):
   - 并行调用 explore agent A: Tier1 Batch A (HN, HuggingFace Papers)
   - 并行调用 explore agent B: Tier1 Batch B (OneUsefulThing, Paul Graham, Dmitry Brant)
   
   等待两个任务完成 → 收集结果
   - 评估总收集数量
   - 计算每个源的耗时

如果 < 35 条高质量:
   第2波 (并行启动):
     - 并行调用 explore agent C: Tier2 Batch A (James Clear, FS Blog)
     - 并行调用 explore agent D: Tier2 Batch B (Stripe Blog, HackerNoon, Scott Young)
     
   等待结果 → 合并到第1波数据
   - 重新评估总数量

如果仍 < 50 条:
   第3波 (并行启动):
     - 并行调用 explore agent E: Tier3 Batch (Product Hunt)
     - WebFetch: ProductHunt 首页（需要完整渲染）
```

#### 并行任务启动

```javascript
// 使用 background_task 并行调用多个 explore agent
async function fetchWithParallelAgents() {
  const taskIds = [];
  
  // 启动第1波（4个并行任务）
  const batch1Tasks = [
    background_task(
      agent="explore",
      description="Fetch HN and HF",
      prompt=`Fetch top 10 from Hacker News and top 3 from HuggingFace Papers.
Return structured JSON with title, summary, url, keywords, quality_score (1-5).
Output format: { status, data: [...], errors: [...], metadata: {...} }`
    ),
    background_task(
      agent="explore",
      description="Fetch blogs",
      prompt=`Fetch latest 3 from Paul Graham and Dmitry Brant.
Return structured JSON with title, summary, url, keywords, quality_score (1-5).
Output format: { status, data: [...], errors: [...], metadata: {...} }`
    )
  ];
  
  taskIds.push(...batch1Tasks.map(t => t.task_id));
  
  // 等待第1波完成
  const batch1Results = await Promise.all(
    taskIds.map(id => background_output({ task_id: id, block: true }))
  );
  
  // 收集数据
  const allItems = [];
  batch1Results.forEach(result => {
    if (result.status === 'success' && result.data) {
      allItems.push(...result.data);
    }
  });
  
  // 评估数量
  if (allItems.length < 35) {
    // 启动第2波
    const batch2Tasks = [
      background_task(
        agent="explore",
        description="Fetch Tier2A sources",
        prompt=`Fetch from James Clear and FS Blog.
Return structured JSON with title, summary, url, keywords, quality_score (1-5).`
      ),
      background_task(
        agent="explore", 
        description="Fetch Tier2B sources",
        prompt=`Fetch from Stripe Blog, HackerNoon, Scott Young.
Return structured JSON with title, summary, url, keywords, quality_score (1-5).`
      )
    ];
    
    taskIds.push(...batch2Tasks.map(t => t.task_id));
    const batch2Results = await Promise.all(
      taskIds.map(id => background_output({ task_id: id, block: true }))
    );
    
    // 合并结果
    batch2Results.forEach(result => {
      if (result.status === 'success' && result.data) {
        allItems.push(...result.data);
      }
    });
  }
  
  // 第3波（如需要）
  if (allItems.length < 50) {
    // 启动第3波：Product Hunt 等 Tier3 源
    const batch3Tasks = [
      background_task(
        agent="explore",
        description="Fetch Product Hunt",
        prompt=`Fetch top 15 from Product Hunt.
Return structured JSON with title, summary, url, keywords, quality_score (1-5).`
      )
    ];
    
    taskIds.push(...batch3Tasks.map(t => t.task_id));
    const batch3Results = await Promise.all(
      taskIds.map(id => background_output({ task_id: id, block: true }))
    );
    
    batch3Results.forEach(result => {
      if (result.status === 'success' && result.data) {
        allItems.push(...result.data);
      }
    });
  }
  
  return { items: allItems, sources_used: taskIds.length };
}
```

#### 进度监控

```javascript
function monitorProgress(taskIds, todayLog) {
  let completed = 0;
  const total = taskIds.length;
  
  // 轮询进度
  const interval = setInterval(() => {
    completed = taskIds.filter(id => {
      const result = background_output({ task_id: id, block: false });
      return result.status === 'done';
    }).length;
    
    // 更新今日日志的phase和summary
    todayLog.run_info.phase = 'fetching';
    todayLog.run_info.worker_count = total;
    todayLog.summary.sources_fetched = completed;
    todayLog.summary.items_collected = total * 5; // 估算
    
    await writeDailyLog(todayLog);
    
    if (completed === total) {
      clearInterval(interval);
    }
  }, 2000); // 每2秒更新一次
}
```

#### 错误处理

```javascript
async function fetchWithErrorHandling(sources, todayLog) {
  const results = [];
  const errors = [];
  
  for (const source of sources) {
    try {
      const result = await fetchFromSource(source);
      
      if (result.status === 'success') {
        results.push(result);
      } else {
        // 标记为失败，但不中断整体流程
        errors.push({
          source_id: source.id,
          error_type: 'fetch_failed',
          error_message: result.error || 'Unknown error',
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      errors.push({
        source_id: source.id,
        error_type: 'network_error',
        error_message: error.message,
        timestamp: new Date().toISOString()
      });
    }
  }
  
  // 记录错误到日志
  todayLog.errors = errors;
  
  return { results, errors };
}
```

#### 性能优化预期

| 指标 | 串行模式 | 并行模式 | 提升 |
|------|---------|---------|------|
| Tier1 抓取 | ~90秒 | ~30秒 | 3x |
| Tier2 抓取 | ~120秒 | ~60秒 | 2x |
| 完整流程（50 items） | ~480秒 | ~180秒 | 2.7x |

**实现关键点**：
1. ✅ 使用 `background_task` 并行调用多个 explore agent
2. ✅ 实时进度监控（每2秒更新）
3. ✅ 动态批次调度（基于已收集数量）
4. ✅ 错误隔离（单个源失败不影响整体）
5. ✅ 预期性能提升：2.7倍（480秒 → 180秒）

### Phase 3: SubAgent 任务格式

每个 SubAgent 接收的任务格式：

```yaml
task: fetch_and_extract
sources:
  - id: hn
    url: https://news.ycombinator.com
    extract: top_10
  - id: hf_papers
    url: https://huggingface.co/papers
    extract: top_voted

output_schema:
  items:
    - source_id: string      # 来源标识
      title: string          # 标题
      summary: string        # 2-4句摘要
      key_points: string[]   # 最多3个要点
      url: string            # 原文链接
      keywords: string[]     # 关键词
      quality_score: 1-5     # 质量评分

constraints:
  filter: "前沿技术/高深技术/提效技术/实用资讯"
  exclude: "泛科普/营销软文/过度学术化/招聘帖"
  max_items_per_source: 10
  skip_on_error: true

return_format: JSON
```

### Phase 4: 主 Agent 监控与反馈

主 Agent 职责：

```yaml
监控:
  - 检查 SubAgent 返回状态 (success/partial/failed)
  - 统计收集到的条目数量
  - 记录每个源的成功率

反馈循环:
  - 如果某 SubAgent 失败，决定是否重试或跳过
  - 如果某源持续失败，标记为禁用
  - 动态调整后续批次的源选择

决策:
   - 条目数 >= 50 且高质量 >= 50 → 停止抓取
   - 条目数 < 35 → 继续下一批
   - 所有批次完成但 < 50 → 用现有内容生成（宁缺毋滥）
```

### Phase 5: 评估与筛选

```yaml
去重:
  - 基于 URL 完全匹配
  - 基于标题相似度 (>80% 视为重复)
  - 检查 cache.json 避免与历史重复

评分校准:
  - 统一各 SubAgent 的评分标准
  - 根据来源可信度调整权重
  - 手动标注的高质量源加分

排序:
   - 按 quality_score 降序
   - 同分按来源优先级排序
   - 截取 Top 50
```

### Phase 6: 浏览器抓取 (MCP Chrome DevTools)

对于需要 JS 渲染的页面，使用无头浏览器：

```yaml
流程:
  1. 调用 mcp__chrome-devtools__new_page 打开页面
  2. 调用 mcp__chrome-devtools__wait_for 等待内容加载
  3. 调用 mcp__chrome-devtools__take_snapshot 获取页面结构
  4. 解析 snapshot 提取所需内容
  5. 调用 mcp__chrome-devtools__close_page 关闭页面

适用场景:
  - ProductHunt (403 on WebFetch)
  - Latent Space (Substack JS 渲染)
  - 其他 SPA 应用
```

### Phase 7: 生成日报

```yaml
输出:
  - 目录: NewsReport/
  - 文件名: YYYY-MM-DD-news-report.md
  - 格式: 标准 Markdown

内容结构:
   - 标题 + 日期
   - 统计摘要（源数量、收录数量）
   - 50条高质量内容（按模板）
   - 生成信息（版本、时间戳）
```

### Phase 8: 更新缓存

```yaml
更新 cache.json:
  - last_run: 记录本次运行信息
  - source_stats: 更新各源统计数据
  - url_cache: 添加已处理的 URL
  - content_hashes: 添加内容指纹
  - article_history: 记录收录文章
```

## SubAgent 调用示例

### 使用 general-purpose Agent

由于自定义 agent 需要 session 重启才能发现，可以使用 general-purpose 并注入 worker prompt：

```
Task 调用:
  subagent_type: general-purpose
  model: haiku
  prompt: |
    你是一个无状态的执行单元。只做被分配的任务，返回结构化 JSON。

    任务：抓取以下 URL 并提取内容

    URLs:
    - https://news.ycombinator.com (提取 Top 10)
    - https://huggingface.co/papers (提取高投票论文)

    输出格式：
    {
      "status": "success" | "partial" | "failed",
      "data": [
        {
          "source_id": "hn",
          "title": "...",
          "summary": "...",
          "key_points": ["...", "...", "..."],
          "url": "...",
          "keywords": ["...", "..."],
          "quality_score": 4
        }
      ],
      "errors": [],
      "metadata": { "processed": 2, "failed": 0 }
    }

    筛选标准：
    - 保留：前沿技术/高深技术/提效技术/实用资讯
    - 排除：泛科普/营销软文/过度学术化/招聘帖

    直接返回 JSON，不要解释。
```

### 使用 worker Agent（需重启 session）

```
Task 调用:
  subagent_type: worker
  prompt: |
task: fetch_and_extract
input:
  urls:
        - https://news.ycombinator.com
        - https://huggingface.co/papers
        - https://stripe.com/blog
        - https://vercel.com/blog
        - https://aws.amazon.com/blogs
    output_schema:
      - source_id: string
      - title: string
      - summary: string
      - key_points: string[]
      - url: string
      - keywords: string[]
      - quality_score: 1-5
    constraints:
      filter: 前沿技术/高深技术/提效技术/实用资讯
      exclude: 泛科普/营销软文/过度学术化
```

## 输出模板

```markdown
# Daily News Report（YYYY-MM-DD）

> 本日筛选自 N 个信息源，共收录 50 条高质量内容
> 生成耗时: X 分钟 | 版本: v3.0
>
> **Warning**: Sub-agent 'worker' not detected. Running in generic mode (Serial Execution). Performance might be degraded.
> **警告**：未检测到 Sub-agent 'worker'。正在以通用模式（串行执行）运行。性能可能会受影响。

---

## 1. 标题

- **摘要**：2-4 行概述
- **要点**：
  1. 要点一
  2. 要点二
  3. 要点三
- **来源**：[链接](URL)
- **关键词**：`keyword1` `keyword2` `keyword3`
- **评分**：⭐⭐⭐⭐⭐ (5/5)

---

## 2. 标题
...

---

*Generated by Daily News Report v3.0*
*Sources: HN, HuggingFace, OneUsefulThing, ...*
```

## 约束与原则

1. **宁缺毋滥**：低质量内容不进入日报
2. **早停机制**：够 20 条高质量就停止抓取
3. **并行优先**：同一批次的 SubAgent 并行执行
4. **失败容错**：单个源失败不影响整体流程
5. **缓存复用**：避免重复抓取相同内容
6. **主 Agent 控制**：所有决策由主 Agent 做出
7. **Fallback Awareness**：检测 sub-agent 可用性，不可用时优雅降级

## 预期性能

| 场景 | 预期时间 | 说明 |
|------|----------|------|
| 最优情况 | ~2 分钟 | Tier1 足够，无需浏览器 |
| 正常情况 | ~3-4 分钟 | 需要 Tier2 补充 |
| 需要浏览器 | ~5-6 分钟 | 包含 JS 渲染页面 |

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| SubAgent 超时 | 记录错误，继续下一个 |
| 源 403/404 | 标记禁用，更新 sources.json |
| 内容提取失败 | 返回原始内容，主 Agent 决定 |
| 浏览器崩溃 | 跳过该源，记录日志 |

## 兼容性与兜底 (Compatibility & Fallback)

为了确保在不同 Agent 环境下的可用性，必须执行以下检查：

1.  **环境检查**:
    -   在 Phase 1 初始化阶段，尝试检测 `worker` sub-agent 是否存在。
    -   如果不存在（或未安装相关插件），自动切换到 **串行执行模式 (Serial Mode)**。

2.  **串行执行模式**:
    -   不使用 parallel block。
    -   主 Agent 依次执行每个源的抓取任务。
    -   虽然速度较慢，但保证基本功能可用。

3.  **用户提示**:
    -   必须在生成的日报开头（引用块部分）包含明显的警告信息，提示用户当前正在运行于降级模式。
