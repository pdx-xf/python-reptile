#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from typing import Dict, Any
from spiders.boss import BossSpider


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    # 检查通用配置文件
    if not os.path.exists("config.py"):
        print("错误：通用配置文件 config.py 不存在！")
        sys.exit(1)

    # 检查项目特定配置文件
    if not os.path.exists("boss_config.py"):
        print("错误：BOSS直聘项目配置文件 boss_config.py 不存在！")
        sys.exit(1)

    try:
        import config
        import boss_config

        # 检查通用配置
        common_configs = [
            "SPIDER_CONFIG",
            "PROXY_CONFIG",
            "BROWSER_CONFIG",
            "LOG_CONFIG",
        ]

        # 检查项目特定配置
        project_configs = [
            "SEARCH_CONFIG",
            "STORAGE_CONFIG",
        ]

        # 验证通用配置
        for config_name in common_configs:
            if not hasattr(config, config_name):
                raise ImportError(f"通用配置文件缺少必要的配置项：{config_name}")

        # 验证项目特定配置
        for config_name in project_configs:
            if not hasattr(boss_config, config_name):
                raise ImportError(f"项目配置文件缺少必要的配置项：{config_name}")

        # 合并配置
        return {
            # 通用配置
            "SPIDER_CONFIG": config.SPIDER_CONFIG,
            "PROXY_CONFIG": config.PROXY_CONFIG,
            "BROWSER_CONFIG": config.BROWSER_CONFIG,
            "LOG_CONFIG": config.LOG_CONFIG,
            # 项目特定配置
            "SEARCH_CONFIG": boss_config.SEARCH_CONFIG,
            "STORAGE_CONFIG": boss_config.STORAGE_CONFIG,
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