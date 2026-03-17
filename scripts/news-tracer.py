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
import re
import urllib.parse

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
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
        
        try:
            # 使用 Bing 搜索新闻
            news_reports = self.search_bing_news(query, days)
        except Exception as e:
            print(f"❌ 搜索失败：{str(e)}")
            return
        
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
        搜索 Bing 新闻
        
        Args:
            query: 搜索关键词
            days: 搜索最近N天
        
        Returns:
            list: 新闻报道列表
        """
        # 构造 Bing 新闻搜索 URL
        encoded_query = urllib.parse.quote(query)
        bing_url = f"https://www.bing.com/news/search?q={encoded_query}&qft=interval%3d\"{days}\"&form=PTFTNR"
        
        # 发送请求
        response = requests.get(bing_url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取新闻条目
        news_items = soup.find_all('div', class_='news-card')
        if not news_items:
            # 尝试其他可能的类名
            news_items = soup.find_all('div', class_='newsitem')
        if not news_items:
            news_items = soup.select('div[class*="news"]')
        
        news_reports = []
        
        for item in news_items:
            try:
                # 提取标题和链接
                title_elem = item.find('a', class_='title') or item.find('a')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                
                # 提取来源
                source_elem = item.find('span', class_='source') or item.find('span', class_='source-name')
                source = source_elem.get_text(strip=True) if source_elem else '未知来源'
                
                # 提取时间
                time_elem = item.find('span', class_='timestamp') or item.find('span', class_='date')
                time_str = time_elem.get_text(strip=True) if time_elem else ''
                
                # 解析时间
                time_obj = self.parse_time(time_str)
                
                news_reports.append({
                    'title': title,
                    'url': url,
                    'source': source,
                    'time': time_obj
                })
                
                # 限制返回数量
                if len(news_reports) >= 20:
                    break
                    
            except Exception as e:
                continue
        
        return news_reports
    
    def parse_time(self, time_str):
        """
        解析时间字符串
        
        Args:
            time_str: 时间字符串（如 "2 hours ago", "2024-03-17"）
        
        Returns:
            datetime: 解析后的时间对象
        """
        if not time_str:
            return None
        
        try:
            # 尝试解析各种时间格式
            if 'ago' in time_str.lower() or '前' in time_str:
                # 处理 "2 hours ago" 或 "2小时前"
                return self.parse_relative_time(time_str)
            else:
                # 处理绝对时间
                return date_parser.parse(time_str)
        except:
            return None
    
    def parse_relative_time(self, time_str):
        """
        解析相对时间（如 "2 hours ago"）
        
        Args:
            time_str: 相对时间字符串
        
        Returns:
            datetime: 解析后的时间对象
        """
        try:
            now = datetime.now()
            
            # 提取数字和单位
            match = re.search(r'(\d+)\s*(hour|minute|day|hour|minute|day)s?\s*(ago|前)', time_str, re.IGNORECASE)
            if not match:
                return now
            
            num = int(match.group(1))
            unit = match.group(2).lower()
            
            # 根据单位计算时间
            if 'hour' in unit:
                delta = timedelta(hours=num)
            elif 'minute' in unit:
                delta = timedelta(minutes=num)
            elif 'day' in unit:
                delta = timedelta(days=num)
            else:
                return now
            
            return now - delta
            
        except:
            return datetime.now()
    
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
