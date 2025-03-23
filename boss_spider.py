from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import pandas as pd
import json
import time
import random


class BossSpider:
    def __init__(self):
        self.base_url = (
            "https://www.zhipin.com/web/geek/job?query=&city=101280600&position=100101"
        )
        self.jobs = []
        self.current_page = 1
        self.max_pages = 10  # 设置最大爬取页数

        try:
            # 配置Chrome选项
            options = webdriver.ChromeOptions()
            options.add_argument(f"user-agent={UserAgent().random}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--lang=zh_CN.UTF-8")  # 添加中文语言支持
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # 使用 Service 对象直接初始化
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=options)

            # 设置窗口大小
            self.driver.set_window_size(1920, 1080)

        except Exception as e:
            print(f"初始化浏览器时出错: {str(e)}")
            raise

    def get_element_text_safely(self, element, class_name):
        """安全地获取元素文本"""
        try:
            return element.find_element(By.CLASS_NAME, class_name).text.strip()
        except NoSuchElementException:
            return "N/A"
        except Exception as e:
            print(f"获取 {class_name} 时出错: {str(e)}")
            return "N/A"

    def wait_for_page_load(self):
        """等待页面加载完成"""
        try:
            # 等待职位列表容器加载完成
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-list-box"))
            )
            # 等待加载动画消失
            WebDriverWait(self.driver, 15).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "loading"))
            )
            return True
        except TimeoutException:
            print("页面加载超时")
            return False

    def click_next_page(self):
        """点击下一页按钮"""
        try:
            # 等待分页区域可见
            pagination = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "options-pages"))
            )

            # 查找下一页按钮
            next_buttons = self.driver.find_elements(
                By.CSS_SELECTOR, ".options-pages a"
            )
            next_button = next_buttons[-1] if next_buttons else None

            if not next_button:
                print("未找到下一页按钮")
                return False

            # 检查是否是最后一页
            if "disabled" in next_button.get_attribute("class"):
                print("已经是最后一页")
                return False

            # 滚动到分页区域
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", pagination
            )
            time.sleep(random.uniform(1, 2))

            # 尝试点击下一页
            try:
                next_button.click()
                print("已点击下一页按钮")

                # 等待页面加载完成
                if self.wait_for_page_load():
                    self.current_page += 1
                    print(f"成功翻到第 {self.current_page} 页")
                    return True
                return False

            except ElementClickInterceptedException:
                # 如果点击被拦截，尝试使用JavaScript点击
                self.driver.execute_script("arguments[0].click();", next_button)
                if self.wait_for_page_load():
                    self.current_page += 1
                    print(f"成功翻到第 {self.current_page} 页")
                    return True
                return False

        except Exception as e:
            print(f"点击下一页按钮时出错: {str(e)}")
            return False

    def get_job_details(self, job_card):
        """获取职位详情页信息"""
        try:
            # 保存当前窗口句柄
            main_window = self.driver.current_window_handle

            # 点击职位卡片
            job_link = job_card.find_element(By.CLASS_NAME, "job-card-left")
            self.driver.execute_script("arguments[0].click();", job_link)

            # 等待新窗口打开
            time.sleep(2)

            # 切换到新窗口
            for window_handle in self.driver.window_handles:
                if window_handle != main_window:
                    self.driver.switch_to.window(window_handle)
                    break

            # 等待详情页加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-sec-text"))
            )

            # 获取详细要求
            try:
                job_description = self.driver.find_element(
                    By.CLASS_NAME, "job-sec-text"
                ).text
            except NoSuchElementException:
                job_description = "未找到详细要求"
            except Exception as e:
                print(f"获取详细要求时出错: {str(e)}")
                job_description = "获取详细要求出错"

            # 关闭当前窗口并切回主窗口
            self.driver.close()
            self.driver.switch_to.window(main_window)

            return job_description

        except Exception as e:
            print(f"获取职位详情时出错: {str(e)}")
            # 确保切回主窗口
            try:
                self.driver.switch_to.window(main_window)
            except:
                pass
            return "获取详情失败"

    def get_job_info(self, test_mode=False):
        try:
            self.driver.get(self.base_url)
            print("正在加载页面...")

            # 等待首页加载完成
            if not self.wait_for_page_load():
                print("首页加载失败")
                return

            while self.current_page <= self.max_pages:
                print(f"正在爬取第 {self.current_page} 页...")
                # 增加页面加载等待时间
                time.sleep(random.uniform(3, 5))

                try:
                    # 等待职位列表加载完成
                    job_list = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_all_elements_located(
                            (By.CLASS_NAME, "job-card-wrapper")
                        )
                    )

                    print(f"找到 {len(job_list)} 个职位信息")

                    # 如果是测试模式，只处理第一个职位
                    if test_mode:
                        job_list = [job_list[0]]
                        print("测试模式：只获取第一个职位信息")

                    for job in job_list:
                        try:
                            # 确保元素完全加载
                            time.sleep(random.uniform(0.5, 1))

                            # 获取基本信息
                            job_info = {
                                "职位": self.get_element_text_safely(job, "job-name"),
                                "薪资": self.get_element_text_safely(job, "salary"),
                                "公司": self.get_element_text_safely(
                                    job, "company-name"
                                ),
                                "地点": self.get_element_text_safely(job, "job-area"),
                                "要求": self.get_element_text_safely(
                                    job, "job-info-tags"
                                ),
                                "公司类型": self.get_element_text_safely(
                                    job, "company-tag-list"
                                ),
                                "页码": self.current_page,
                            }

                            # 获取详细要求
                            print(f"正在获取 {job_info['职位']} 的详细要求...")
                            job_info["详细要求"] = self.get_job_details(job)

                            self.jobs.append(job_info)
                            print(f"成功解析职位: {job_info['职位']}")

                            # 每获取一个职位详情后保存一次数据
                            self.save_to_json()

                            # 如果是测试模式，获取一个职位后就退出
                            if test_mode:
                                print("测试模式：已获取一个职位信息，退出爬取")
                                return

                        except Exception as e:
                            print(f"解析单个职位信息时出错: {str(e)}")
                            continue

                    # 如果不是测试模式，继续翻页
                    if not test_mode:
                        if not self.click_next_page():
                            print("已到达最后一页或无法继续翻页")
                            break

                        # 翻页后额外等待
                        time.sleep(random.uniform(2, 3))
                    else:
                        break

                except TimeoutException:
                    print("等待职位列表加载超时")
                    break
                except Exception as e:
                    print(f"获取职位列表时出错: {str(e)}")
                    break

        except Exception as e:
            print(f"爬取过程出错: {str(e)}")
        finally:
            self.driver.quit()

    def save_to_json(self):
        try:
            with open("jobs.json", "w", encoding="utf-8") as f:
                json.dump(self.jobs, f, ensure_ascii=False, indent=2)
            print(f"成功保存 {len(self.jobs)} 条职位信息到 jobs.json")
            # 同时保存为Excel
            self.save_to_excel()
        except Exception as e:
            print(f"保存数据时出错: {str(e)}")

    def save_to_excel(self):
        """将职位信息保存为Excel文件"""
        try:
            # 将数据转换为DataFrame
            df = pd.DataFrame(self.jobs)

            # 设置Excel写入器，使用openpyxl引擎以支持.xlsx格式
            with pd.ExcelWriter("jobs.xlsx", engine="openpyxl") as writer:
                # 将DataFrame写入Excel
                df.to_excel(writer, index=False, sheet_name="职位信息")

                # 自动调整列宽
                worksheet = writer.sheets["职位信息"]
                for idx, col in enumerate(df.columns):
                    # 获取列的最大宽度
                    max_length = max(
                        df[col].astype(str).apply(len).max(),  # 数据的最大长度
                        len(str(col)),  # 列名的长度
                    )
                    # 设置列宽（稍微增加一点宽度以便更好地显示）
                    worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2

            print(f"成功保存 {len(self.jobs)} 条职位信息到 jobs.xlsx")
        except Exception as e:
            print(f"保存Excel文件时出错: {str(e)}")


if __name__ == "__main__":
    spider = BossSpider()
    spider.get_job_info(test_mode=False)
