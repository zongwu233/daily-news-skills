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

def create_daily_log_for_today():
    """为今天创建日志"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    run_id = f"run_{date_str}_001"
    
    # 创建日志数据结构
    log_data = {
        "schema_version": "2.0",
        "description": "Daily News Report 每日运行日志",
        
        "run_info": {
            "date": date_str,
            "run_id": run_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration_seconds": 0,
            "phase": "initializing"
        },
        
        "summary": {
            "sources_fetched": 0,
            "items_collected": 0,
            "items_published": 0,
            "items_deduped": 0,
            "quality_avg": 0.0,
            "status": "pending"
        },
        
        "sources": {
            "hn": {"status": "pending", "items_collected": 0, "avg_quality": 0.0},
            "hf_papers": {"status": "pending", "items_collected": 0, "avg_quality": 0.0},
            "producthunt": {"status": "pending", "items_collected": 0, "avg_quality": 0.0},
            "hackernoon_pm": {"status": "pending", "items_collected": 0, "avg_quality": 0.0},
            "jamesclear": {"status": "pending", "items_collected": 0, "avg_quality": 0.0},
            "fs_blog": {"status": "pending", "items_collected": 0, "avg_quality": 0.0},
            "scottyoung": {"status": "pending", "items_collected": 0, "avg_quality": 0.0},
            "stripe_blog": {"status": "pending", "items_collected": 0, "avg_quality": 0.0},
            "paulgraham": {"status": "pending", "items_collected": 0, "avg_quality": 0.0},
            "dmitrybrant": {"status": "pending", "items_collected": 0, "avg_quality": 0.0}
        },
        
        "url_cache": {
            "comment": "本日抓取的所有URL，用于去重",
            "urls": []
        },
        
        "content_hashes": {
            "comment": "内容指纹，用于跨日去重",
            "hashes": {}
        },
        
        "articles": {
            "comment": "本日收录的所有文章数据",
            "items": []
        },
        
        "errors": {
            "comment": "运行过程中的所有错误信息",
            "items": []
        },
        
        "metadata": {
            "environment": "local",
            "agent_version": "3.0",
            "worker_count": 1,
            "parallel_enabled": False
        }
    }
    
    return log_data

def update_index_file():
    """更新索引文件"""
    # 创建或读取索引
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    else:
        index_data = {
            "schema_version": "2.0",
            "description": "Daily News Report 缓存系统索引文件",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_runs": 0,
            "available_dates": []
        }
    
    # 更新可用日期
    date_str = datetime.now().strftime("%Y-%m-%d")
    available_dates = set(index_data.get("available_dates", []))
    available_dates.add(date_str)
    index_data["available_dates"] = sorted(list(available_dates), reverse=True)
    index_data["total_runs"] = index_data.get("total_runs", 0) + 1
    index_data["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 保存索引
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 索引文件已更新: {len(index_data['available_dates'])} 个可用日期")

def main():
    """主迁移流程"""
    print("=" * 60)
    print("🔄 Daily News Report 缓存系统初始化")
    print("=" * 60)
    
    # 创建日志目录
    log_dir = CACHE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    print(f"📁 创建日志目录: {log_dir}")
    
    # 为今天创建日志
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_data = create_daily_log_for_today()
    log_file = log_dir / f"{date_str}.json"
    
    # 保存日志
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 创建今日日志: {log_file}")
    
    # 更新索引文件
    update_index_file()
    
    print("\n" + "=" * 60)
    print(f"✅ 缓存系统初始化完成！")
    print(f"   - 索引文件: {INDEX_FILE}")
    print(f"   - 日志目录: {log_dir}")
    print(f"   - 今日日志: {log_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
