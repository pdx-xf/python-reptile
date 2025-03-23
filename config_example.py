# BOSS直聘爬虫配置文件示例
# 使用方法：将此文件复制为 config.py 并根据需要修改配置

# 搜索参数配置
SEARCH_CONFIG = {
    "keywords": ["Python", "Java", "前端"],  # 搜索关键词列表
    "city": "深圳",                         # 城市
    "salary_range": {                       # 薪资范围
        "min": 0,                           # 最低薪资（K）
        "max": 100                          # 最高薪资（K）
    },
    "experience": "不限",                    # 经验要求：不限/应届生/1-3年/3-5年/5-10年/10年以上
    "degree": "不限",                        # 学历要求：不限/大专/本科/硕士/博士
    "finance_stage": "不限",                 # 融资阶段：不限/未融资/天使轮/A轮/B轮/C轮/D轮及以上/已上市/不需要融资
    "company_size": "不限",                  # 公司规模：不限/0-20人/20-99人/100-499人/500-999人/1000-9999人/10000人以上
}

# 爬虫行为配置
SPIDER_CONFIG = {
    "max_pages": 10,                        # 最大爬取页数
    "delay": {                              # 延时配置（秒）
        "min": 3,                           # 最小延时
        "max": 5                            # 最大延时
    },
    "retry": {                              # 重试配置
        "max_attempts": 3,                  # 最大重试次数
        "delay": 5                          # 重试间隔（秒）
    },
    "timeout": 30                           # 页面加载超时时间（秒）
}

# 数据存储配置
STORAGE_CONFIG = {
    "json_file": "jobs.json",               # JSON文件保存路径
    "csv_enabled": True,                    # 是否同时保存为CSV
    "csv_file": "jobs.csv",                 # CSV文件保存路径
    "excel_enabled": False,                 # 是否同时保存为Excel
    "excel_file": "jobs.xlsx"              # Excel文件保存路径
}

# 代理配置
PROXY_CONFIG = {
    "enabled": False,                       # 是否启用代理
    "proxy_file": "proxies.txt",           # 代理文件路径
    "proxy_type": "http",                  # 代理类型：http/https/socks5
    "check_proxy": True,                   # 是否检查代理可用性
    "proxy_timeout": 10                    # 代理超时时间（秒）
}

# 浏览器配置
BROWSER_CONFIG = {
    "headless": False,                     # 是否启用无头模式
    "user_agent_rotate": True,             # 是否轮换User-Agent
    "image_loading": False,                # 是否加载图片
    "window_size": {                       # 浏览器窗口大小
        "width": 1920,
        "height": 1080
    }
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",                       # 日志级别：DEBUG/INFO/WARNING/ERROR
    "file": "spider.log",                  # 日志文件路径
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # 日志格式
} 