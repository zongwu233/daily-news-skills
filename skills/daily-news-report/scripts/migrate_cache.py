#!/usr/bin/env python3
"""
Daily News Report 缓存迁移脚本
将旧版 cache.json 迁移到新的日志系统
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 配置
CACHE_DIR = Path(__file__).parent.parent / "cache"
OLD_CACHE_FILE = CACHE_DIR.parent / "cache.json"
INDEX_FILE = CACHE_DIR / "index.json"

def load_old_cache():
    """加载旧版缓存数据"""
    if not OLD_CACHE_FILE.exists():
        print(f"⚠️  旧缓存文件不存在: {OLD_CACHE_FILE}")
        return None
    
    with open(OLD_CACHE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_daily_log(old_data, date_str):
    """从旧数据创建每日日志"""
    
    # 生成run_id
    run_id = f"run_{date_str}_migrated_001"
    
    # 创建日志数据结构
    log_data = {
        "schema_version": "2.0",
        "description": "Daily News Report 每日运行日志 - 迁移版本",
        
        "run_info": {
            "date": date_str,
            "run_id": run_id,
            "timestamp": f"{date_str}T12:00:00Z",
            "duration_seconds": old_data.get("last_run", {}).get("duration_seconds", 0),
            "phase": "done"
        },
        
        "summary": {
            "sources_fetched": len(old_data.get("sources_used", [])),
            "items_collected": old_data.get("last_run", {}).get("items_collected", 0),
            "items_published": old_data.get("last_run", {}).get("items_published", 0),
            "items_deduped": 0,  # 旧数据无此字段
            "quality_avg": calculate_avg_quality(old_data),
            "status": "migrated"
        },
        
        "sources": migrate_sources(old_data, date_str),
        "url_cache": migrate_urls(old_data, date_str),
        "content_hashes": migrate_hashes(old_data),
        "articles": migrate_articles(old_data, date_str),
        "errors": [],
        "metadata": {
            "environment": "local",
            "agent_version": "2.0",
            "worker_count": 1,
            "parallel_enabled": False
        }
    }
    
    return log_data

def calculate_avg_quality(old_data):
    """计算平均质量分"""
    source_stats = old_data.get("source_stats", {})
    total_quality = 0
    total_items = 0
    
    for source_id, stats in source_stats.items():
        avg_q = stats.get("avg_quality_score", 0)
        items = stats.get("avg_items_per_fetch", 0)
        total_quality += avg_q * items
        total_items += items
    
    return round(total_quality / total_items, 2) if total_items > 0 else 0.0

def migrate_sources(old_data, date_str):
    """迁移源统计信息"""
    sources = {}
    
    # 从article_history提取文章来源
    article_history = old_data.get("article_history", {})
    articles_by_source = {}
    
    for date, articles in article_history.items():
        for article in articles:
            # 根据文章标题推断来源
            title = article.get("title", "")
            source_id = infer_source_from_title(title)
            if source_id not in articles_by_source:
                articles_by_source[source_id] = []
            articles_by_source[source_id].append(article)
    
    # 构建sources数据
    source_stats = old_data.get("source_stats", {})
    
    for source_id in ["hn", "hf_papers", "producthunt", "hackernoon_pm", 
                   "jamesclear", "fs_blog", "scottyoung", "stripe_blog",
                   "paulgraham", "dmitrybrant"]:
        sources[source_id] = {
            "status": "migrated",
            "items_collected": len(articles_by_source.get(source_id, [])),
            "items_published": len(articles_by_source.get(source_id, [])),
            "avg_quality": source_stats.get(source_id, {}).get("avg_quality_score", 0.0),
            "duration_ms": 0,
            "error": None,
            "urls_fetched": []
        }
    
    return sources

def infer_source_from_title(title):
    """从文章标题推断来源"""
    title_lower = title.lower()
    
    if "xai" in title_lower or "spacex" in title_lower:
        return "spacex"
    elif "codex" in title_lower:
        return "openai"
    elif "anki" in title_lower:
        return "anki"
    elif "github" in title_lower or "sudo" in title_lower or "moltbook" in title_lower:
        return "github"
    elif "nano-vllm" in title_lower or "zig" in title_lower or "rclone" in title_lower:
        return "hackernews_tech"
    elif "ebisu" in title_lower or "adaptive" in title_lower or "fs-researcher" in title_lower:
        return "huggingface"
    elif "moltbook" in title_lower or "chaching" in title_lower or "amara" in title_lower:
        return "producthunt"
    elif "metronome" in title_lower or "stripe" in title_lower or "agentic" in title_lower:
        return "stripe_blog"
    elif "3-2-1" in title_lower:
        return "jamesclear"
    elif "independence" in title_lower or "energy" in title_lower:
        return "fs_blog"
    elif "stress" in title_lower or "energy" in title_lower or "learn taste" in title_lower:
        return "scottyoung"
    elif "alignment" in title_lower or "stakeholders" in title_lower or "broken" in title_lower or "ideaops" in title_lower:
        return "hackernoon_pm"
    elif "largest number" in title_lower or "game arena" in title_lower:
        return "google_deepmind"
    elif "how we went" in title_lower or "design review" in title_lower:
        return "hackernoon_pm"
    elif "businesses grow" in title_lower or "introducing" in title_lower:
        return "stripe_blog"
    else:
        return "unknown"

def migrate_urls(old_data, date_str):
    """迁移URL缓存"""
    url_cache = old_data.get("url_cache", {}).get("entries", {})
    
    return {
        "comment": f"从旧系统迁移的URL缓存 - {date_str}",
        "urls": list(url_cache.keys())
    }

def migrate_hashes(old_data):
    """迁移内容指纹"""
    content_hashes = old_data.get("content_hashes", {}).get("entries", {})
    
    return {
        "comment": "从旧系统迁移的内容指纹",
        "hashes": content_hashes
    }

def migrate_articles(old_data, date_str):
    """迁移文章数据"""
    article_history = old_data.get("article_history", {})
    
    # 获取指定日期的文章
    articles = article_history.get(date_str, [])
    
    # 为每篇文章添加元数据
    articles_with_metadata = []
    for idx, title in enumerate(articles, 1):
        articles_with_metadata.append({
            "id": idx,
            "title": title,
            "source_id": infer_source_from_title(title),
            "url": f"https://example.com/article/{idx}",  # 旧数据无URL
            "summary": "Migrated from old cache",
            "key_points": [],
            "keywords": [],
            "quality_score": 4,
            "fetched_at": f"{date_str}T12:00:00Z"
        })
    
    return {
        "comment": f"从旧系统迁移的文章 - {date_str}",
        "items": articles_with_metadata
    }

def update_index_file(old_data):
    """更新索引文件"""
    # 读取现有索引或创建新的
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    else:
        index_data = {
            "schema_version": "2.0",
            "description": "Daily News Report 缓存系统索引文件",
            "last_updated": "2026-02-03T12:00:00Z",
            "total_runs": 0,
            "available_dates": []
        }
    
    # 更新总运行次数
    index_data["total_runs"] = index_data.get("total_runs", 0) + len(old_data.get("article_history", {}))
    
    # 更新可用日期列表
    available_dates = set(index_data.get("available_dates", []))
    for date in old_data.get("article_history", {}).keys():
        available_dates.add(date)
    index_data["available_dates"] = sorted(list(available_dates), reverse=True)
    
    # 更新最后更新时间
    index_data["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 保存索引
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 索引文件已更新: {len(index_data['available_dates'])} 个可用日期")

def main():
    """主迁移流程"""
    print("=" * 60)
    print("🔄 Daily News Report 缓存迁移工具")
    print("=" * 60)
    
    # 加载旧缓存
    old_cache = load_old_cache()
    if old_cache is None:
        print("❌ 无法迁移：旧缓存文件不存在")
        return
    
    print(f"📂 加载旧缓存: {OLD_CACHE_FILE}")
    
    # 获取文章历史
    article_history = old_cache.get("article_history", {})
    print(f"📊 发现 {len(article_history)} 天的历史数据")
    
    # 迁移每个日期
    migrated_count = 0
    for date_str, articles in article_history.items():
        print(f"\n🔄 迁移日期: {date_str} ({len(articles)} 篇文章)")
        
        # 创建日志目录
        log_dir = CACHE_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 创建每日日志文件
        log_data = create_daily_log(old_cache, date_str)
        log_file = log_dir / f"{date_str}.json"
        
        # 保存日志
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 创建日志: {log_file}")
        migrated_count += 1
    
    # 更新索引文件
    update_index_file(old_cache)
    
    print("\n" + "=" * 60)
    print(f"✅ 迁移完成！")
    print(f"   - 迁移日期数: {migrated_count}")
    print(f"   - 索引文件: {INDEX_FILE}")
    print(f"   - 日志目录: {CACHE_DIR / 'logs/'}")
    print("=" * 60)
    
    # 备份旧缓存
    backup_file = OLD_CACHE_FILE.with_suffix('.json.backup')
    old_cache.rename(backup_file)
    print(f"💾 旧缓存已备份到: {backup_file}")

if __name__ == "__main__":
    main()
