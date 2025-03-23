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
from utils.city_mapping import get_city_id


class BossSpider(BaseSpider):
    """Boss直聘爬虫"""

    def build_search_url(self, keyword: str = "") -> str:
        """根据搜索配置构建URL

        Args:
            keyword: 搜索关键词，默认为空字符串
        """
        search_config = self.config["SEARCH_CONFIG"]
        if not keyword and search_config["keywords"]:
            keyword = search_config["keywords"][0]

        city_id = get_city_id(search_config["city"])
        if not city_id:
            self.logger.error(f"未找到城市 {search_config['city']} 的ID映射")
            raise ValueError(f"未找到城市 {search_config['city']} 的ID映射")

        return f"https://www.zhipin.com/web/geek/job?query={keyword}&city={city_id}"

    def wait_for_page_load(self) -> bool:
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

    def click_next_page(self) -> bool:
        """点击下一页按钮"""
        try:
            pagination = WebDriverWait(
                self.driver, self.config["SPIDER_CONFIG"]["timeout"]
            ).until(EC.presence_of_element_located((By.CLASS_NAME, "options-pages")))

            next_buttons = self.driver.find_elements(
                By.CSS_SELECTOR, ".options-pages a"
            )
            next_button = next_buttons[-1] if next_buttons else None

            if not next_button:
                self.logger.warning("未找到下一页按钮")
                return False

            if "disabled" in next_button.get_attribute("class"):
                self.logger.info("已经是最后一页")
                return False

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", pagination
            )
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

    def get_job_details(self, job_card) -> str:
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
                job_description = self.driver.find_element(
                    By.CLASS_NAME, "job-sec-text"
                ).text
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

    def run(self) -> None:
        """运行爬虫"""
        try:
            self.logger.info("开始爬取数据")

            for keyword in self.config["SEARCH_CONFIG"]["keywords"]:
                self.logger.info(f"开始爬取关键词：{keyword}")
                self.current_page = 1

                self.base_url = self.build_search_url(keyword)
                self.driver.get(self.base_url)
                if not self.wait_for_page_load():
                    continue

                while self.current_page <= self.max_pages:
                    self.logger.info(f"正在爬取第 {self.current_page} 页...")
                    self.random_delay()

                    try:
                        job_list = WebDriverWait(
                            self.driver, self.config["SPIDER_CONFIG"]["timeout"]
                        ).until(
                            EC.presence_of_all_elements_located(
                                (By.CLASS_NAME, "job-card-wrapper")
                            )
                        )

                        self.logger.info(f"找到 {len(job_list)} 个职位信息")

                        for job in job_list:
                            try:
                                self.random_delay()

                                job_info = {
                                    "职位": self.get_element_text_safely(
                                        job, "job-name"
                                    ),
                                    "薪资": self.get_element_text_safely(job, "salary"),
                                    "公司": self.get_element_text_safely(
                                        job, "company-name"
                                    ),
                                    "地点": self.get_element_text_safely(
                                        job, "job-area"
                                    ),
                                    "要求": self.get_element_text_safely(
                                        job, "job-info-tags"
                                    ),
                                    "公司类型": self.get_element_text_safely(
                                        job, "company-tag-list"
                                    ),
                                    "页码": self.current_page,
                                    "搜索关键词": keyword,
                                }

                                self.logger.info(
                                    f"正在获取 {job_info['职位']} 的详细要求..."
                                )
                                job_info["详细要求"] = self.get_job_details(job)

                                self.data.append(job_info)
                                self.logger.info(f"成功解析职位: {job_info['职位']}")

                                if len(self.data) % 10 == 0:
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

            self.save_data()
            self.logger.info("数据爬取完成")

        except Exception as e:
            self.logger.error(f"爬虫运行出错: {str(e)}")
            raise
        finally:
            self.cleanup()
