#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import json
import pandas as pd
import logging
from spiders.base import BaseSpider

class TestBaseSpider(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试配置
        self.test_config = {
            "STORAGE_CONFIG": {
                "json_file": "test_data.json",
                "csv_file": "test_data.csv",
                "excel_file": "test_data.xlsx",
                "csv_enabled": True,
                "excel_enabled": True
            },
            "LOG_CONFIG": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "test_spider.log"
            },
            "BROWSER_CONFIG": {
                "headless": True,
                "image_loading": True,
                "window_size": {
                    "width": 1920,
                    "height": 1080
                }
            },
            "PROXY_CONFIG": {
                "enabled": False,
                "proxy_file": "proxies.txt",
                "check_proxy": False,
                "proxy_timeout": 5
            },
            "SPIDER_CONFIG": {
                "max_pages": 1,
                "timeout": 10,
                "delay": {
                    "min": 1,
                    "max": 3
                }
            }
        }
        
        # 创建测试数据
        self.test_data = [
            {"name": "测试1", "age": 25, "city": "北京"},
            {"name": "测试2", "age": 30, "city": "上海"},
            {"name": "测试3", "age": 28, "city": "广州"}
        ]
        
        # 创建爬虫实例
        self.spider = BaseSpider(self.test_config)
        self.spider.data = self.test_data

    def tearDown(self):
        """测试后的清理工作"""
        # 关闭所有日志处理器
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        
        # 清理测试文件
        test_files = [
            os.path.join("data", "test_data.json"),
            os.path.join("data", "test_data.csv"),
            os.path.join("data", "test_data.xlsx"),
            "test_spider.log"
        ]
        
        for file in test_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                print(f"删除文件 {file} 时出错: {str(e)}")
        
        # 清理data目录（如果为空）
        try:
            if os.path.exists("data") and not os.listdir("data"):
                os.rmdir("data")
        except Exception as e:
            print(f"删除data目录时出错: {str(e)}")
        
        # 清理爬虫资源
        self.spider.cleanup()

    def test_save_data(self):
        """测试数据保存功能"""
        # 调用保存方法
        self.spider.save_data()
        
        # 验证data目录是否存在
        self.assertTrue(os.path.exists("data"), "data目录应该被创建")
        
        # 验证JSON文件
        json_path = os.path.join("data", "test_data.json")
        self.assertTrue(os.path.exists(json_path), "JSON文件应该被创建")
        with open(json_path, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.test_data, "JSON数据应该与测试数据一致")
        
        # 验证CSV文件
        csv_path = os.path.join("data", "test_data.csv")
        self.assertTrue(os.path.exists(csv_path), "CSV文件应该被创建")
        df = pd.read_csv(csv_path)
        self.assertEqual(len(df), len(self.test_data), "CSV数据行数应该与测试数据一致")
        
        # 验证Excel文件
        excel_path = os.path.join("data", "test_data.xlsx")
        self.assertTrue(os.path.exists(excel_path), "Excel文件应该被创建")
        df = pd.read_excel(excel_path)
        self.assertEqual(len(df), len(self.test_data), "Excel数据行数应该与测试数据一致")

if __name__ == "__main__":
    unittest.main() 