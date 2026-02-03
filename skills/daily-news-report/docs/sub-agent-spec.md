# Daily News Report - Sub-Agent 任务规范

## 任务格式

每个 sub-agent 必须返回符合此结构的数据：

```json
{
  "task_id": "unique_task_id",
  "status": "success" | "partial" | "failed",
  "data": [
    {
      "source_id": "hn",
      "title": "文章标题",
      "summary": "2-4句摘要，包含核心观点和价值",
      "key_points": [
        "要点1：最多50字符",
        "要点2：最多50字符",
        "要点3：最多50字符"
      ],
      "url": "完整URL",
      "keywords": ["keyword1", "keyword2"],
      "quality_score": 1-5 (整数评分),
      "fetched_at": "ISO 8601 timestamp",
      "timestamp": "2026-02-03T12:00:00Z"
    }
  ],
  "errors": [
    {
      "source_id": "hn",
      "error_type": "fetch_failed" | "parse_failed" | "network_error",
      "error_message": "详细错误信息",
      "timestamp": "ISO 8601 timestamp"
    }
  ],
  "metadata": {
    "processed": 10,
    "failed": 0,
    "duration_ms": 5000,
    "retry_count": 0,
    "agent_version": "3.0"
  }
}
```

## 质量评分标准

| 评分 | 描述 | 示例 |
|------|------|------|
| 5 | 必看、深度、原创性 | Anthropic 研究论文、创始人深度文章 |
| 4 | 有价值、有见地 | 高质量技术博客、实用教程 |
| 3 | 一般、普通内容 | 普通技术新闻、一般产品 |
| 2 | 信息量少、深度不够 | 简短新闻、产品介绍 |
| 1 | 低质量、营销软文 | 招聘广告、纯营销内容 |

## 筛选标准

### 必须包含
- 前沿技术 / 深度思考 / 实用技巧 / 高质量产品

### 排除
- 招聘信息（"Who is hiring"）
- 纯广告营销
- 过度商业化内容
- 无技术深度的泛科普

## 子Agent 分配策略

### Batch 1: Tier1 高优先级（并行）
```
SubAgent A: Hacker News (top 10)
  - 优先：高价值、技术深度
  - 预期产出：6-8 条高质量

SubAgent B: HuggingFace Papers (top 3)
  - 优先：前沿研究、AI 论文
  - 预期产出：2-3 条高质量

SubAgent C: Paul Graham (latest 3)
  - 优先：深度思考、创业见解
  - 预期产出：2-3 条高质量

SubAgent D: Dmitry Brant (latest 1)
  - 优先：技术考古、逆向工程
  - 预期产出：1 条高质量
```

### Batch 2: Tier2 中优先级（并行，如需要）
```
SubAgent E: James Clear (latest 1)
  - 优先：个人成长、习惯养成
  - 预期产出：1 条高质量

SubAgent F: FS Blog (latest 1)
  - 优先：思维模型、决策智慧
  - 预期产出：1 条高质量

SubAgent G: Product Hunt (top 10)
  - 优先：新产品、创新工具
  - 预期产出：4-6 条高质量

SubAgent H: Stripe Blog (top 5)
  - 优先：FinTech、支付技术
  - 预期产出：3-5 条高质量
```

### Batch 3: Tier3 低优先级（如需要）
```
其他 Tier3 源...
```

## 错误处理

### 重试策略
- 网络错误：重试 1 次，然后标记失败
- 解析错误：跳过该源，记录错误
- 超时：30秒超时，标记失败

### 日志级别
- DEBUG: 请求/响应详情
- INFO: 关键操作（源开始/结束、数据统计）
- WARN: 非致命错误（不影响整体运行）
- ERROR: 致命错误（影响运行）

## 返回格式

所有 sub-agent 必须返回纯 JSON，无 Markdown 格式。
最后使用 `return` 或 `console.log()` 输出。
