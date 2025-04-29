#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)
from .base import BaseSpider
import time


class BiQuGeSpider(BaseSpider):
    """笔趣阁爬虫"""
    
    def run(self) -> None:
        """运行爬虫"""
        self.logger.info("开始爬取笔趣阁")
        # https://b3b.zibq.cc/html/225172/list.html
        self.search_url = "https://b3b.zibq.cc/html/225172/list.html"
        self.driver.get(self.search_url)
        self.random_delay()
        
        try:
            zj_list = WebDriverWait(self.driver, self.config["SPIDER_CONFIG"]["timeout"]).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".book_last dl dd a"))
            )
        except TimeoutException:
            self.logger.error("获取章节列表超时")
            return
        
        zj_list = zj_list[1:]
        for zj in zj_list:
            print(zj.text)
            start_time = time.time()
            # 点击zj在另一个窗口打开
            zj_url = zj.get_attribute("href")
            self.driver.execute_script("window.open('{}');".format(zj_url))
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.random_delay()
            # 获取章节内容
            content = self.driver.find_element(By.ID, "chaptercontent").text
            print(content)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.random_delay()
            # 计算花了多少时间
            end_time = time.time()
            print(f"花了{end_time - start_time}秒")
