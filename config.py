# 公共配置文件

# 爬虫行为配置
SPIDER_CONFIG = {
    "max_pages": 1,  # 最大爬取页数
    "delay": {"min": 3, "max": 5},  # 延时配置（秒）
    "retry": {  # 重试配置
        "max_attempts": 3,  # 最大重试次数
        "delay": 5,  # 重试间隔（秒）
    },
    "timeout": 30,  # 页面加载超时时间（秒）
}

# 代理配置
PROXY_CONFIG = {
    "enabled": True,  # 是否启用代理
    "proxy_file": "proxies.txt",  # 代理文件路径
    "proxy_type": "http",  # 代理类型：http/https/socks5
    "check_proxy": True,  # 是否检查代理可用性
    "proxy_timeout": 10,  # 代理超时时间（秒）
}

# 浏览器配置
BROWSER_CONFIG = {
    "headless": True,  # 是否启用无头模式
    "user_agent_rotate": True,  # 是否轮换User-Agent
    "image_loading": True,  # 是否加载图片
    "window_size": {"width": 1920, "height": 1080},  # 浏览器窗口大小
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",  # 日志级别：DEBUG/INFO/WARNING/ERROR
    "file": "./logs/spider.log",  # 日志文件路径
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
} 