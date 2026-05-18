import requests
import json
from datetime import datetime

# 微信推送（不填也能运行）
SEND_KEY = ""

# 国内指数估值区间
VAL = {
    "hs300": {"low_pe":9, "high_pe":14},
    "zz500": {"low_pe":13, "high_pe":20},
    "cybz": {"low_pe":25, "high_pe":38}
}

indexs = {
    "hs300":"000300",
    "zz500":"000905",
    "cybz":"399006"
}

result = {"date": datetime.now().strftime("%Y-%m-%d")}
headers = {"User-Agent":"Mozilla/5.0"}

# 爬取数据
for name,code in indexs.items():
    try:
        r = requests.get(f"https://www.csindex.com.cn/zh/index-data/index-pe-pb?indexCode={code}", headers=headers, timeout=10)
        d = r.json()
        result[f"{name}_pe"] = float(d["data"][0]["pe"])
    except:
        result[f"{name}_pe"] = None

# 历史数据
try:
    with open("history.json","r",encoding="utf-8") as f:
        history = json.load(f)
except:
    history = []
history.append(result)
history = history[-90:]

# 保存
with open("history.json","w",encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)
with open("data.json","w",encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ 数据生成成功")
