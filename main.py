#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from typing import Dict, Any
from spiders.boss import BossSpider


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not os.path.exists("config.py"):
        print("错误：配置文件 config.py 不存在！")
        print("请复制 config_example.py 为 config.py 并根据需要修改配置。")
        sys.exit(1)

    try:
        import config

        required_configs = [
            "SEARCH_CONFIG",
            "SPIDER_CONFIG",
            "STORAGE_CONFIG",
            "PROXY_CONFIG",
            "BROWSER_CONFIG",
            "LOG_CONFIG",
        ]

        for config_name in required_configs:
            if not hasattr(config, config_name):
                raise ImportError(f"配置文件缺少必要的配置项：{config_name}")

        return {
            "SEARCH_CONFIG": config.SEARCH_CONFIG,
            "SPIDER_CONFIG": config.SPIDER_CONFIG,
            "STORAGE_CONFIG": config.STORAGE_CONFIG,
            "PROXY_CONFIG": config.PROXY_CONFIG,
            "BROWSER_CONFIG": config.BROWSER_CONFIG,
            "LOG_CONFIG": config.LOG_CONFIG,
        }
    except ImportError as e:
        print(f"错误：配置文件格式错误！\n{str(e)}")
        sys.exit(1)


def main():
    """主函数"""
    try:
        config = load_config()
        spider = BossSpider(config)
        spider.run()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 