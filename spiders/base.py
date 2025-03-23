#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from typing import Dict, Any, List
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
from fake_useragent import UserAgent
import pandas as pd
import requests


class BaseSpider:
    """爬虫基类，提供所有爬虫共享的基础功能"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化爬虫

        Args:
            config: 配置字典，包含所有配置项
        """
        self.config = config
        self.setup_logging()
        self.logger.info("爬虫初始化开始")
        self.setup_browser()
        self.logger.info("爬虫初始化完成")

        self.data = []
        self.current_page = 1
        self.max_pages = self.config["SPIDER_CONFIG"]["max_pages"]

    def setup_logging(self) -> None:
        """配置日志"""
        log_config = self.config["LOG_CONFIG"]
        logging.basicConfig(
            level=getattr(logging, log_config["level"]),
            format=log_config["format"],
            handlers=[
                logging.FileHandler(log_config["file"], encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_user_agent(self) -> str:
        """获取合适的 User-Agent

        Returns:
            str: 合适的 User-Agent 字符串
        """
        ua = UserAgent()
        desktop_ua = ua.chrome
        if not desktop_ua:
            desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        mobile_keywords = ["Mobile", "Android", "iPhone", "iPad", "Windows Phone"]
        if any(keyword in desktop_ua for keyword in mobile_keywords):
            self.logger.warning("检测到移动端 User-Agent，尝试重新获取桌面端 User-Agent")
            return desktop_ua

        return desktop_ua

    def setup_browser(self) -> None:
        """配置浏览器"""
        browser_config = self.config["BROWSER_CONFIG"]
        chrome_options = Options()

        if browser_config["headless"]:
            chrome_options.add_argument("--headless")

        if not browser_config["image_loading"]:
            chrome_options.add_argument("--blink-settings=imagesEnabled=false")

        user_agent = self.get_user_agent()
        chrome_options.add_argument(f"user-agent={user_agent}")
        self.logger.info(f"使用 User-Agent: {user_agent}")

        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-usb-keyboard-detect")
        chrome_options.add_argument("--disable-usb-discovery")

        chrome_options.add_argument(
            f"--window-size={browser_config['window_size']['width']},{browser_config['window_size']['height']}"
        )

        if self.config["PROXY_CONFIG"]["enabled"]:
            proxy = self.get_proxy()
            if proxy:
                chrome_options.add_argument(f"--proxy-server={proxy}")

        try:
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager

            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.logger.error(f"使用webdriver_manager安装ChromeDriver失败: {str(e)}")
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                self.logger.error(f"创建Chrome浏览器实例失败: {str(e)}")
                raise

    def get_proxy(self) -> str:
        """获取代理地址"""
        proxy_config = self.config["PROXY_CONFIG"]
        if not os.path.exists(proxy_config["proxy_file"]):
            self.logger.warning(f"代理文件 {proxy_config['proxy_file']} 不存在")
            return ""

        try:
            with open(proxy_config["proxy_file"], "r") as f:
                proxies = f.readlines()

            if not proxies:
                return ""

            proxy = random.choice(proxies).strip()

            if proxy_config["check_proxy"]:
                if not self.check_proxy(proxy):
                    return ""

            return proxy
        except Exception as e:
            self.logger.error(f"获取代理出错: {str(e)}")
            return ""

    def check_proxy(self, proxy: str) -> bool:
        """检查代理是否可用"""
        try:
            response = requests.get(
                "https://www.baidu.com",
                proxies={"http": proxy, "https": proxy},
                timeout=self.config["PROXY_CONFIG"]["proxy_timeout"],
            )
            return response.status_code == 200
        except:
            return False

    def get_element_text_safely(self, element, class_name: str) -> str:
        """安全地获取元素文本"""
        try:
            return element.find_element(By.CLASS_NAME, class_name).text.strip()
        except NoSuchElementException:
            return "N/A"
        except Exception as e:
            self.logger.error(f"获取 {class_name} 时出错: {str(e)}")
            return "N/A"

    def wait_for_page_load(self, timeout: int = None) -> bool:
        """等待页面加载完成"""
        if timeout is None:
            timeout = self.config["SPIDER_CONFIG"]["timeout"]
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True
        except TimeoutException:
            self.logger.error("页面加载超时")
            return False

    def random_delay(self) -> None:
        """随机延时"""
        delay_config = self.config["SPIDER_CONFIG"]["delay"]
        time.sleep(random.uniform(delay_config["min"], delay_config["max"]))

    def save_data(self) -> None:
        """保存数据到文件"""
        storage_config = self.config["STORAGE_CONFIG"]

        # 保存JSON
        try:
            with open(storage_config["json_file"], "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            self.logger.info(
                f"成功保存 {len(self.data)} 条数据到 {storage_config['json_file']}"
            )
        except Exception as e:
            self.logger.error(f"保存JSON文件时出错: {str(e)}")

        # 转换为DataFrame
        df = pd.DataFrame(self.data)

        # 保存CSV
        if storage_config["csv_enabled"]:
            try:
                df.to_csv(storage_config["csv_file"], index=False, encoding="utf-8-sig")
                self.logger.info(f"成功保存数据到 {storage_config['csv_file']}")
            except Exception as e:
                self.logger.error(f"保存CSV文件时出错: {str(e)}")

        # 保存Excel
        if storage_config["excel_enabled"]:
            try:
                with pd.ExcelWriter(
                    storage_config["excel_file"], engine="openpyxl"
                ) as writer:
                    df.to_excel(writer, index=False, sheet_name="数据")
                    worksheet = writer.sheets["数据"]
                    for idx, col in enumerate(df.columns):
                        max_length = max(
                            df[col].astype(str).apply(len).max(), len(str(col))
                        )
                        worksheet.column_dimensions[chr(65 + idx)].width = (
                            max_length + 2
                        )
                self.logger.info(f"成功保存数据到 {storage_config['excel_file']}")
            except Exception as e:
                self.logger.error(f"保存Excel文件时出错: {str(e)}")

    def cleanup(self) -> None:
        """清理资源"""
        if hasattr(self, "driver"):
            self.driver.quit()
        self.logger.info("爬虫资源已清理")

    def run(self) -> None:
        """运行爬虫（需要在子类中实现）"""
        raise NotImplementedError("子类必须实现run方法") 