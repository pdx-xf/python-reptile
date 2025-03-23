#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from typing import Dict, Any
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

class BossSpider:
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
        
        self.jobs = []
        self.current_page = 1
        self.max_pages = self.config["SPIDER_CONFIG"]["max_pages"]

    def build_search_url(self, keyword: str = "") -> str:
        """根据搜索配置构建URL
        
        Args:
            keyword: 搜索关键词，默认为空字符串
        """
        search_config = self.config["SEARCH_CONFIG"]
        # 如果没有提供关键词，使用第一个配置的关键词
        if not keyword and search_config["keywords"]:
            keyword = search_config["keywords"][0]
        return f"https://www.zhipin.com/web/geek/job?query={keyword}&city={search_config['city']}"

    def setup_logging(self) -> None:
        """配置日志"""
        log_config = self.config["LOG_CONFIG"]
        logging.basicConfig(
            level=getattr(logging, log_config["level"]),
            format=log_config["format"],
            handlers=[
                logging.FileHandler(log_config["file"], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("BossSpider")

    def setup_browser(self) -> None:
        """配置浏览器"""
        browser_config = self.config["BROWSER_CONFIG"]
        chrome_options = Options()
        
        if browser_config["headless"]:
            chrome_options.add_argument("--headless")
        
        if not browser_config["image_loading"]:
            chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        
        if browser_config["user_agent_rotate"]:
            chrome_options.add_argument(f"user-agent={UserAgent().random}")
        
        chrome_options.add_argument(f"--window-size={browser_config['window_size']['width']},{browser_config['window_size']['height']}")
        
        # 添加代理配置
        if self.config["PROXY_CONFIG"]["enabled"]:
            proxy = self.get_proxy()
            if proxy:
                chrome_options.add_argument(f'--proxy-server={proxy}')
        
        try:
            # 尝试使用新版本的ChromeDriver安装方式
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = ChromeService(ChromeDriverManager(os_type="win32").install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.logger.error(f"使用webdriver_manager安装ChromeDriver失败: {str(e)}")
            try:
                # 回退到直接使用Chrome
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
                proxies={
                    "http": proxy,
                    "https": proxy
                },
                timeout=self.config["PROXY_CONFIG"]["proxy_timeout"]
            )
            return response.status_code == 200
        except:
            return False

    def get_element_text_safely(self, element, class_name):
        """安全地获取元素文本"""
        try:
            return element.find_element(By.CLASS_NAME, class_name).text.strip()
        except NoSuchElementException:
            return "N/A"
        except Exception as e:
            self.logger.error(f"获取 {class_name} 时出错: {str(e)}")
            return "N/A"

    def wait_for_page_load(self):
        """等待页面加载完成"""
        try:
            timeout = self.config["SPIDER_CONFIG"]["timeout"]
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-list-box"))
            )
            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "loading"))
            )
            return True
        except TimeoutException:
            self.logger.error("页面加载超时")
            return False

    def random_delay(self):
        """随机延时"""
        delay_config = self.config["SPIDER_CONFIG"]["delay"]
        time.sleep(random.uniform(delay_config["min"], delay_config["max"]))

    def click_next_page(self):
        """点击下一页按钮"""
        try:
            pagination = WebDriverWait(self.driver, self.config["SPIDER_CONFIG"]["timeout"]).until(
                EC.presence_of_element_located((By.CLASS_NAME, "options-pages"))
            )

            next_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".options-pages a")
            next_button = next_buttons[-1] if next_buttons else None

            if not next_button:
                self.logger.warning("未找到下一页按钮")
                return False

            if "disabled" in next_button.get_attribute("class"):
                self.logger.info("已经是最后一页")
                return False

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination)
            self.random_delay()

            try:
                next_button.click()
                self.logger.info("已点击下一页按钮")

                if self.wait_for_page_load():
                    self.current_page += 1
                    self.logger.info(f"成功翻到第 {self.current_page} 页")
                    return True
                return False

            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", next_button)
                if self.wait_for_page_load():
                    self.current_page += 1
                    self.logger.info(f"成功翻到第 {self.current_page} 页")
                    return True
                return False

        except Exception as e:
            self.logger.error(f"点击下一页按钮时出错: {str(e)}")
            return False

    def get_job_details(self, job_card):
        """获取职位详情页信息"""
        main_window = self.driver.current_window_handle
        try:
            job_link = job_card.find_element(By.CLASS_NAME, "job-card-left")
            self.driver.execute_script("arguments[0].click();", job_link)
            self.random_delay()

            for window_handle in self.driver.window_handles:
                if window_handle != main_window:
                    self.driver.switch_to.window(window_handle)
                    break

            WebDriverWait(self.driver, self.config["SPIDER_CONFIG"]["timeout"]).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-sec-text"))
            )

            try:
                job_description = self.driver.find_element(By.CLASS_NAME, "job-sec-text").text
            except Exception as e:
                self.logger.error(f"获取详细要求时出错: {str(e)}")
                job_description = "获取详细要求出错"

            self.driver.close()
            self.driver.switch_to.window(main_window)
            return job_description

        except Exception as e:
            self.logger.error(f"获取职位详情时出错: {str(e)}")
            try:
                self.driver.switch_to.window(main_window)
            except:
                pass
            return "获取详情失败"

    def save_data(self):
        """保存数据到文件"""
        storage_config = self.config["STORAGE_CONFIG"]
        
        # 保存JSON
        try:
            with open(storage_config["json_file"], "w", encoding="utf-8") as f:
                json.dump(self.jobs, f, ensure_ascii=False, indent=2)
            self.logger.info(f"成功保存 {len(self.jobs)} 条职位信息到 {storage_config['json_file']}")
        except Exception as e:
            self.logger.error(f"保存JSON文件时出错: {str(e)}")

        # 转换为DataFrame
        df = pd.DataFrame(self.jobs)
        
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
                with pd.ExcelWriter(storage_config["excel_file"], engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="职位信息")
                    # 自动调整列宽
                    worksheet = writer.sheets["职位信息"]
                    for idx, col in enumerate(df.columns):
                        max_length = max(
                            df[col].astype(str).apply(len).max(),
                            len(str(col))
                        )
                        worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
                self.logger.info(f"成功保存数据到 {storage_config['excel_file']}")
            except Exception as e:
                self.logger.error(f"保存Excel文件时出错: {str(e)}")

    def run(self) -> None:
        """运行爬虫"""
        try:
            self.logger.info("开始爬取数据")
            
            # 遍历所有关键词
            for keyword in self.config["SEARCH_CONFIG"]["keywords"]:
                self.logger.info(f"开始爬取关键词：{keyword}")
                self.current_page = 1
                
                # 使用当前关键词构建URL
                self.base_url = self.build_search_url(keyword)
                
                self.driver.get(self.base_url)
                if not self.wait_for_page_load():
                    continue

                while self.current_page <= self.max_pages:
                    self.logger.info(f"正在爬取第 {self.current_page} 页...")
                    self.random_delay()

                    try:
                        job_list = WebDriverWait(self.driver, self.config["SPIDER_CONFIG"]["timeout"]).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "job-card-wrapper"))
                        )

                        self.logger.info(f"找到 {len(job_list)} 个职位信息")

                        for job in job_list:
                            try:
                                self.random_delay()

                                job_info = {
                                    "职位": self.get_element_text_safely(job, "job-name"),
                                    "薪资": self.get_element_text_safely(job, "salary"),
                                    "公司": self.get_element_text_safely(job, "company-name"),
                                    "地点": self.get_element_text_safely(job, "job-area"),
                                    "要求": self.get_element_text_safely(job, "job-info-tags"),
                                    "公司类型": self.get_element_text_safely(job, "company-tag-list"),
                                    "页码": self.current_page,
                                    "搜索关键词": keyword
                                }

                                self.logger.info(f"正在获取 {job_info['职位']} 的详细要求...")
                                job_info["详细要求"] = self.get_job_details(job)

                                self.jobs.append(job_info)
                                self.logger.info(f"成功解析职位: {job_info['职位']}")

                                # 定期保存数据
                                if len(self.jobs) % 10 == 0:
                                    self.save_data()

                            except Exception as e:
                                self.logger.error(f"解析单个职位信息时出错: {str(e)}")
                                continue

                        if not self.click_next_page():
                            self.logger.info("已到达最后一页或无法继续翻页")
                            break

                    except TimeoutException:
                        self.logger.error("等待职位列表加载超时")
                        break
                    except Exception as e:
                        self.logger.error(f"获取职位列表时出错: {str(e)}")
                        break

            # 最终保存所有数据
            self.save_data()
            self.logger.info("数据爬取完成")
            
        except Exception as e:
            self.logger.error(f"爬虫运行出错: {str(e)}")
            raise
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """清理资源"""
        if hasattr(self, 'driver'):
            self.driver.quit()
        self.logger.info("爬虫资源已清理")

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not os.path.exists("config.py"):
        print("错误：配置文件 config.py 不存在！")
        print("请复制 config_example.py 为 config.py 并根据需要修改配置。")
        sys.exit(1)

    try:
        import config
        required_configs = [
            "SEARCH_CONFIG", "SPIDER_CONFIG", "STORAGE_CONFIG",
            "PROXY_CONFIG", "BROWSER_CONFIG", "LOG_CONFIG"
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
            "LOG_CONFIG": config.LOG_CONFIG
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
