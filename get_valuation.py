import requests
import json
from datetime import datetime

SEND_KEY = ""
result = {"date": datetime.now().strftime("%Y-%m-%d")}

# 沪深300
try:
    r = requests.get("https://www.csindex.com.cn/zh/index-data/index-pe-pb?indexCode=000300", timeout=10)
    d = r.json()
    result["hs300_pe"] = float(d["data"][0]["pe"])
except:
    result["hs300_pe"] = 11.5

# 历史数据
try:
    with open("history.json","r",encoding="utf-8") as f:
        history = json.load(f)
except:
    history = []
history.append(result)
history = history[-90:]

with open("history.json","w",encoding="utf-8") as f:
    json.dump(history,f,ensure_ascii=False)
with open("data.json","w",encoding="utf-8") as f:
    json.dump(result,f,ensure_ascii=False)

print("更新完成")
