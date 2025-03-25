# Python 爬虫框架

这是一个基于 Python 的通用爬虫框架，支持多种网站的爬取。目前支持 Boss 直聘等网站的爬取。

## 项目结构

```
python-reptile/
├── spiders/                 # 爬虫目录
│   ├── __init__.py
│   ├── base.py             # 基础爬虫类
│   └── boss.py             # Boss直聘爬虫
├── utils/                   # 工具类目录
│   ├── __init__.py
│   └── city_mapping.py     # 城市映射工具
├── data/                    # 数据存储目录
├── logs/                    # 日志目录
├── config.py               # 配置文件
├── config_example.py       # 配置文件示例
├── main.py                 # 主程序入口
└── README.md              # 项目说明文档
```

## 功能特点

- 支持多种网站的爬取
- 可配置的爬虫行为
- 支持代理 IP
- 支持无头浏览器
- 支持多种数据存储格式（JSON/CSV/Excel）
- 完善的日志记录
- 异常处理和重试机制

## 安装环境（推荐使用 uv）

```bash
scoop install uv
# on mac
brew install uv
```

## 安装依赖

```bash
uv sync
```

## 使用方法

1. 修改配置文件 `config.py`，根据需要调整配置项

2. 修改特定项目配置文件

3. 运行爬虫：

```bash
uv run main.py
```

## 添加新的爬虫

1. 在 `spiders` 目录下创建新的爬虫类文件
2. 继承 `BaseSpider` 类
3. 实现必要的方法（至少实现 `run` 方法）
4. 在 `main.py` 中导入并使用新的爬虫类

## 配置说明

### 搜索配置 (SEARCH_CONFIG)

- keywords: 搜索关键词列表
- city: 城市名称

### 爬虫配置 (SPIDER_CONFIG)

- max_pages: 每个关键词最大爬取页数
- timeout: 页面加载超时时间
- delay: 延迟时间范围

### 存储配置 (STORAGE_CONFIG)

- json_file: JSON 文件路径
- csv_enabled: 是否保存 CSV
- csv_file: CSV 文件路径
- excel_enabled: 是否保存 Excel
- excel_file: Excel 文件路径

### 代理配置 (PROXY_CONFIG)

- enabled: 是否启用代理
- proxy_file: 代理文件路径
- check_proxy: 是否检查代理可用性
- proxy_timeout: 代理检查超时时间

### 浏览器配置 (BROWSER_CONFIG)

- headless: 是否使用无头模式
- image_loading: 是否加载图片
- window_size: 窗口大小

### 日志配置 (LOG_CONFIG)

- level: 日志级别
- format: 日志格式
- file: 日志文件路径

## 注意事项

1. 请遵守网站的 robots.txt 规则
2. 建议使用代理 IP，避免被封禁
3. 适当设置延迟时间，避免请求过于频繁
4. 定期备份数据文件

## 贡献指南

1. Fork 本仓库
2. 创建新的分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License
