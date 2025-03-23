# BOSS直聘爬虫配置文件

# 搜索参数配置
SEARCH_CONFIG = {
    "keywords": ["Python", "Java", "前端"],  # 搜索关键词列表
    "city": "深圳",  # 城市
    "salary_range": {  # 薪资范围
        "min": 0,  # 最低薪资（K）
        "max": 100,  # 最高薪资（K）
    },
    "experience": "不限",  # 经验要求：不限/应届生/1-3年/3-5年/5-10年/10年以上
    "degree": "不限",  # 学历要求：不限/大专/本科/硕士/博士
    "finance_stage": "不限",  # 融资阶段：不限/未融资/天使轮/A轮/B轮/C轮/D轮及以上/已上市/不需要融资
    "company_size": "不限",  # 公司规模：不限/0-20人/20-99人/100-499人/500-999人/1000-9999人/10000人以上
}

# 数据存储配置
STORAGE_CONFIG = {
    "json_file": "jobs.json",  # JSON文件保存路径
    "csv_enabled": False,  # 是否同时保存为CSV
    "csv_file": "jobs.csv",  # CSV文件保存路径
    "excel_enabled": True,  # 是否同时保存为Excel
    "excel_file": "jobs.xlsx",  # Excel文件保存路径
}
