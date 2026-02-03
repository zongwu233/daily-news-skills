#!/usr/bin/env node
/**
 * 同步Markdown报告到Astro项目
 * 从 skills/daily-news-report/NewsReport/ 目录同步到 website/src/content/reports/
 */

const fs = require('fs');
const path = require('path');

// 配置
const NEWS_REPORT_DIR = path.join(__dirname, '../NewsReport');
const WEBSITE_CONTENT_DIR = path.join(__dirname, '../website/src/content/reports');

function ensureDir(dirPath) {
    if (!fs.existsSync(dirPath)) {
        console.log(`📁 创建目录: ${dirPath}`);
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

function syncReports() {
    console.log('=' * 60);
    console.log('🔄 开始同步 Daily News Report 到网站');
    console.log('=' * 60);
    
    // 确保目录存在
    ensureDir(WEBSITE_CONTENT_DIR);
    
    // 读取所有报告
    const files = fs.readdirSync(NEWS_REPORT_DIR)
      .filter(file => file.endsWith('.md'))
      .sort()
      .reverse(); // 最新的在前
    
    console.log(`📊 发现 ${files.length} 个报告文件`);
    
    let synced = 0;
    let skipped = 0;
    
    for (const file of files) {
        const sourcePath = path.join(NEWS_REPORT_DIR, file);
        const targetPath = path.join(WEBSITE_CONTENT_DIR, file);
        
        // 检查目标是否已存在且较新
        let shouldSync = true;
        if (fs.existsSync(targetPath)) {
            const sourceStat = fs.statSync(sourcePath);
            const targetStat = fs.statSync(targetPath);
            
            if (targetStat.mtimeMs >= sourceStat.mtimeMs) {
                console.log(`  跳过: ${file} (目标文件较新或相同)`);
                skipped++;
                shouldSync = false;
            }
        }
        
        if (shouldSync) {
            // 复制文件
            fs.copyFileSync(sourcePath, targetPath);
            console.log(`  ✅ 同步: ${file}`);
            synced++;
        }
    }
    
    console.log('\n' + '=' * 60);
    console.log(`✅ 同步完成！`);
    console.log(`   - 同步: ${synced} 个文件`);
    console.log(`   - 跳过: ${skipped} 个文件`);
    console.log(`   - 源目录: ${NEWS_REPORT_DIR}`);
    console.log(`   - 目标目录: ${WEBSITE_CONTENT_DIR}`);
    console.log('=' * 60);
    
    return { synced, skipped, total: files.length };
}

// 如果直接运行此脚本
if (require.main === module) {
    const result = syncReports();
    process.exit(result.synced > 0 ? 0 : 1);
}

module.exports = { syncReports, ensureDir };
