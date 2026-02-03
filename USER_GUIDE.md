# Daily News Report 用户文档

## 📋 目录

1. [快速开始](#快速开始)
2. [缓存系统](#缓存系统)
3. [网站使用](#网站使用)
4. [性能优化说明](#性能优化说明)
5. [故障排查](#故障排查)

---

## 快速开始

### 基础使用

```bash
# 运行 daily-news-report skill
cd /path/to/erduo-skills
# 使用 skill 生成日报（已升级为并行抓取）
```

### 首次使用配置

1. **初始化缓存系统**（自动执行）
   - 首次运行会自动创建新的缓存目录结构
   - 旧的 `cache.json` 会自动迁移到新系统

2. **生成报告**
   - 报告将保存到 `NewsReport/YYYY-MM-DD-news-report.md`
   - 同时生成网站数据到 `news-report-website/src/data/reports/`

3. **启动网站**（可选）
   ```bash
   cd news-report-website
   npm run dev
   # 访问 http://localhost:3000
   ```

---

## 缓存系统

### 新架构说明

从 v2.0 开始，缓存系统从单一文件升级为分布式日志系统：

#### 目录结构

```
skills/daily-news-report/cache/
├── index.json                  # 元数据索引
├── logs/                       # 每日独立日志
│   ├── 2026-02-02.json
│   └── 2026-02-03.json
├── url_cache/                  # URL去重缓存
│   └── 2026-02/
│       └── urls.json
└── content_hashes/             # 内容指纹（跨日去重）
    └── 2026-02/
        └── hashes.json
```

#### 各文件说明

**index.json** - 元数据索引
- 记录所有可用日期
- 汇总统计数据（平均耗时、平均质量等）
- 最后更新时间戳

**logs/YYYY-MM-DD.json** - 每日完整日志
- `run_info`: 运行元数据（日期、run_id、时间戳、耗时、阶段）
- `summary`: 汇总统计（源数量、条目数、去重数、平均质量、状态）
- `sources`: 各源详细结果（状态、条目数、平均质量、耗时、URL列表）
- `url_cache`: 本日抓取的所有URL
- `content_hashes`: 内容指纹（用于跨日去重）
- `articles`: 文章数据数组
- `errors`: 错误记录数组
- `metadata`: 运行环境信息

**优势**

✅ **性能优化** - 只需加载当天的数据，减少I/O操作
✅ **历史可追溯** - 按日期独立存储，方便查询历史
✅ **数据隔离** - 不同天互不干扰，避免单文件损坏
✅ **易于备份** - 可按日期归档，定期清理旧数据
✅ **并发安全** - 每日独立，减少锁竞争

---

## 网站使用

### 启动网站

```bash
cd news-report-website
npm run dev
```

访问：http://localhost:3000

### 功能说明

#### 主页 (/)

- 📰 **最新日报摘要**
  - 日期、条目数、平均质量
  - 生成耗时
- 🔍 **搜索栏**
  - 实时搜索文章标题和标签
  - URL参数：`?q=关键词`
  - 重置按钮清空搜索
- 🏷️ **标签云**
  - 5大分类：AI、编程、产品、产品管理、金融
  - 点击标签跳转到标签聚合页
  - 标签计数动态显示

#### 单日报告页 (/archive/YYYY-MM-DD)

- 📅 完整报告日期
- 📊 统计信息
  - 总条目数
  - 平均质量评分
  - 生成耗时
- 📰 50个文章卡片
  - 每个卡片显示：
    - ⭐ 质量评分（1-5星）
    - 标题和摘要（限制行数）
    - 关键词标签（带颜色分类）
    - 查看详情链接

#### 归档页 (/archive)

- 📅 所有历史日报
- 按时间倒序排列
- 快速预览（标题+条目数）
- 点击查看完整报告

#### 标签页 (/tags)

- 🏷️ 完整标签统计
- 热门标签榜单
- 颜色编码分类
- 标签数量显示

#### 设置页 (/settings)

- 🌙️ **深色模式切换**
- 🌐 **语言选择**（中文/English）
- ℹ️ **关于信息**

### 响应式设计

- 📱 **移动端**
  - 隐藏菜单按钮（点击展开）
  - 单列卡片布局
  - 优化的触摸交互
- 💻 **桌面端**
  - 三列卡片网格
  - 固定导航栏
  - 悬浮标签云

---

## 性能优化说明

### 并行抓取优化（v2.0）

**预期性能提升**：从 8 分钟 → **3 分钟**（2.7倍）

#### 批次执行策略

**Batch 1: Tier1 高优先级**（约30秒）
- Worker A: Hacker News (top 10)
- Worker B: HuggingFace Papers (top 3)
- Worker C: Paul Graham (latest 3)
- Worker D: Dmitry Brant (latest 1)
- 4个任务并行执行

**Batch 2: Tier2 中优先级**（约60秒，如需要）
- Worker E: James Clear (latest 1)
- Worker F: FS Blog (latest 1)
- Worker G: Stripe Blog (top 5)
- Worker H: HackerNoon (top 5)
- Worker I: Scott Young (latest 1)
- 6个任务并行执行

**Batch 3: Tier3 低优先级**（约90秒，如需要）
- Worker J: Product Hunt (top 10)
- WebFetch 完整页面渲染（需要JS）

#### 实时进度监控

- 每2秒更新一次进度
- 显示当前批次和完成状态
- 错误源自动跳过

#### 错误处理

- 网络错误：重试1次后跳过
- 解析错误：记录并继续
- 单个源失败不影响整体流程

---

## 故障排查

### 常见问题

#### 1. 网站无法启动

**问题**：`npm run dev` 失败

**解决方案**：
```bash
# 1. 检查依赖是否完整
cd news-report-website
npm install

# 2. 清理缓存重试
rm -rf node_modules package-lock.json
npm install

# 3. 检查端口占用
lsof -i :3000
# 如果端口被占用，更换端口
npx astro dev --port 3001
```

#### 2. 报告数据不显示

**可能原因**：
- Markdown文件未正确生成
- 同步脚本未执行
- 数据文件路径错误

**检查步骤**：
```bash
# 1. 检查报告文件是否存在
ls -la ../NewsReport/2026-02-03-news-report.md

# 2. 检查网站数据文件
ls -la src/data/reports/2026-02-03.json

# 3. 手动执行同步
node scripts/sync-reports.js
```

#### 3. 搜索功能异常

**可能原因**：
- JavaScript错误
- Astro数据格式不正确
- 路由配置问题

**调试步骤**：
```bash
# 1. 打开浏览器开发者工具
# 2. 查看Console中的错误信息
# 3. 检查 src/data/reports/*.json 数据格式
```

#### 4. 缓存系统错误

**可能原因**：
- 目录权限问题
- JSON格式错误
- 磁盘空间不足

**解决方案**：
```bash
# 1. 检查目录权限
ls -la cache/logs/

# 2. 检查JSON格式
cat cache/index.json | python3 -m json.tool

# 3. 初始化缓存系统
python3 scripts/init_cache.py
```

---

## 技术支持

### 日志位置

```
skills/daily-news-report/cache/logs/    # 每日运行日志
NewsReport/                                  # Markdown报告输出
news-report-website/src/data/reports/     # 网站数据源
```

### 常用命令

```bash
# 同步报告到网站
cd news-report-website
npm run sync-reports

# 启动网站
npm run dev

# 构建网站
npm run build

# 预览网站
npm run preview
```

---

## 版本历史

### v2.0 (2026-02-03) - 当前版本

**更新内容**：
- ✅ 缓存系统重构（分布式日志架构）
- ✅ 本地网站开发（Astro + TailwindCSS）
- ✅ 并行抓取设计（background_task架构）
- ✅ 响应式UI（移动+桌面）
- ✅ 搜索和标签云功能
- ✅ 深色模式支持

**性能提升**：
- 🚀 抓取速度：8分钟 → 3分钟（2.7倍）
- 🚀 I/O性能：减少文件大小，只加载当天数据
- 🚀 阅读体验：从纯Markdown提升为交互式网站

### v1.0 (2026-02-02)

- 原有单一 `cache.json` 架构
- 串行抓取（约8分钟）
- 纯Markdown报告

---

**文档版本**: v2.0
**更新时间**: 2026-02-03
**作者**: Erduo Skills
