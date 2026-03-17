#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
News Tracer - 新闻溯源和真实性验证工具
Author: 王小瑶
"""

import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as date_parser

class NewsTracer:
    """新闻溯源器"""
    
    # 权威媒体列表
    authoritative_sites = [
        'reuters.com',
        'bloomberg.com',
        'apnews.com',
        'wsj.com',
        'nytimes.com',
        'ft.com',
        'cnbc.com',
        'bbc.com'
    ]
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def trace(self, query, days=7):
        """
        追踪新闻来源
        
        Args:
            query: 新闻关键词
            days: 搜索最近N天（默认7天）
        """
        print(f"📰 新闻溯源报告\n")
        print(f"🔍 搜索关键词：{query}\n")
        print("⏱️ 时间线：\n")
        
        # 使用 Bing 搜索新闻
        news_reports = self.search_bing_news(query, days)
        
        if not news_reports:
            print("❌ 未找到相关新闻报道")
            return
        
        # 按时间排序
        news_reports.sort(key=lambda x: x.get('time', datetime.min))
        
        # 显示时间线
        for idx, report in enumerate(news_reports, 1):
            self.display_report(idx, report)
        
        # 真实性评估
        self.assess_credibility(news_reports)
    
    def search_bing_news(self, query, days):
        """
        搜索 Bing 新闻（简化版）
        
        实际使用时，需要：
        1. 访问 Bing 新闻搜索页面
        2. 提取所有新闻链接和时间
        3. 按时间排序
        
        这里返回示例数据用于演示
        """
        # TODO: 实现 Bing 新闻搜索
        # 返回示例数据
        return []
    
    def display_report(self, idx, report):
        """显示单篇报道"""
        time_str = self.format_time(report.get('time'))
        title = report.get('title', '未知标题')
        source = report.get('source', '未知来源')
        url = report.get('url', '')
        
        print(f"[{idx}] {time_str}")
        print(f"   📰 {title}")
        print(f"   🌐 来源：{source}")
        print(f"   🔗 网址：{url}")
        
        if idx == 1:
            print("   ✅ 最早来源")
        
        print()
    
    def assess_credibility(self, reports):
        """评估新闻真实性"""
        print("📊 真实性评估：\n")
        
        total_reports = len(reports)
        sources = set(report.get('source', '') for report in reports)
        authoritative_count = sum(
            1 for report in reports
            if any(site in report.get('url', '') for site in self.authoritative_sites)
        )
        
        print(f"📰 报道数量：{total_reports} 篇")
        print(f"🌐 来源数量：{len(sources)} 个")
        print(f"⭐ 权威媒体：{authoritative_count}")
        print()
        
        # 结论
        if authoritative_count > 0:
            print("🎯 结论：✅ 新闻可信度高（有权威媒体报道）")
        elif total_reports > 3:
            print("🎯 结论：⚠️ 新闻可能真实，但缺乏权威媒体报道")
        else:
            print("🎯 结论：❌ 新闻真实性存疑（报道来源少）")
        
        print()
    
    def format_time(self, time_obj):
        """格式化时间显示"""
        if not time_obj:
            return "未知时间"
        
        if isinstance(time_obj, str):
            try:
                time_obj = date_parser.parse(time_obj)
            except:
                return time_obj
        
        return time_obj.strftime("%Y-%m-%d %H:%M")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法：python3 news-tracer.py '新闻关键词'")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    tracer = NewsTracer()
    tracer.trace(query)

if __name__ == '__main__':
    main()
