import requests
import json
from datetime import datetime

# 配置指数代码（可自己加：沪深300、中证500、创业板、红利等）
index_list = [
    {"name": "沪深300", "code": "000300"},
    {"name": "中证500", "code": "000905"},
    {"name": "创业板指", "code": "399006"}
]

result = []
today = datetime.now().strftime("%Y-%m-%d")

for idx in index_list:
    # 示例：用公开指数PE接口，你可替换为更准数据源
    try:
        # 简易模拟估值（实际可替换东方财富/理杏仁/中证指数接口）
        pe = round(10 + (hash(idx["code"] + today) % 15)/2, 2)
        pb = round(1.2 + (hash(idx["code"]) % 3)/10, 2)
        
        # 自动判断估值高低（分位逻辑：<30%低估，30-70%正常，>70%高估）
        if pe < 12:
            level = "低估"
            color = "#009944"
        elif pe < 18:
            level = "正常"
            color = "#ff9900"
        else:
            level = "高估"
            color = "#dd2222"
            
        result.append({
            "date": today,
            "name": idx["name"],
            "pe": pe,
            "pb": pb,
            "level": level,
            "color": color
        })
    except:
        pass

# 保存数据
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
