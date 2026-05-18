import requests
import json
from datetime import datetime

# ========== 配置区 ==========
SEND_KEY = ""

VAL = {
    "hs300":   {"low_pe":9,  "mid_pe":11, "high_pe":14, "low_pct":20, "high_pct":80},
    "zz500":   {"low_pe":13, "mid_pe":16, "high_pe":20, "low_pct":20, "high_pct":80},
    "cybz":    {"low_pe":25, "mid_pe":30, "high_pe":38, "low_pct":20, "high_pct":80},
    "zzhl":    {"low_pe":7,  "mid_pe":9,  "high_pe":12, "low_pct":20, "high_pct":80},
    "kc50":    {"low_pe":30, "mid_pe":38, "high_pe":48, "low_pct":20, "high_pct":80},
    "sz50":    {"low_pe":8,  "mid_pe":10, "high_pe":13, "low_pct":20, "high_pct":80},
    "zz1000":  {"low_pe":18, "mid_pe":22, "high_pe":28, "low_pct":20, "high_pct":80}
}
# ==========================

cn_index = {
    "hs300": "000300","zz500":"000905","cybz":"399006",
    "zzhl":"000922","kc50":"000688","sz50":"000016","zz1000":"000852"
}

result = {"date": datetime.now().strftime("%Y-%m-%d")}
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# 只爬国内指数，稳定不报错
for name, code in cn_index.items():
    try:
        url = f"https://www.csindex.com.cn/zh/index-data/index-pe-pb?indexCode={code}"
        r = requests.get(url, headers=headers, timeout=12)
        d = r.json()
        result[f"{name}_pe"] = float(d["data"][0]["pe"])
        result[f"{name}_pb"] = float(d["data"][0]["pb"])
    except:
        result[f"{name}_pe"] = None
        result[f"{name}_pb"] = None

# 加载历史
try:
    with open("history.json","r",encoding="utf-8") as f:
        history = json.load(f)
except:
    history = []
history.append(result)
history = history[-180:]

# 计算百分位
for name in list(VAL.keys()):
    plist = [x[f"{name}_pe"] for x in history if x.get(f"{name}_pe") is not None]
    if plist:
        current = result[f"{name}_pe"]
        pct = sum(1 for p in plist if p <= current) / len(plist) * 100
        result[f"{name}_pct"] = round(pct,1)
    else:
        result[f"{name}_pct"] = None

# 保存文件
with open("history.json","w",encoding="utf-8") as f:
    json.dump(history,f,ensure_ascii=False,indent=2)
with open("data.json","w",encoding="utf-8") as f:
    json.dump(result,f,ensure_ascii=False,indent=2)

# 微信推送
if SEND_KEY:
    msg = "📊 全指数估值每日更新\n"
    for name in cn_index:
        pe = result.get(f"{name}_pe")
        pct = result.get(f"{name}_pct")
        if pe is None: continue
        v = VAL[name]
        if pe <= v["low_pe"] or pct <= v["low_pct"]:
            status = "🔥【买入】低估"
        elif pe >= v["high_pe"] or pct >= v["high_pct"]:
            status = "⚠️【卖出】高估"
        else:
            status = "✅ 正常持有"
        msg += f"{name} PE:{pe:.2f} 分位:{pct}% {status}\n"
    requests.get(f"https://sctapi.ftqq.com/{SEND_KEY}.send?title=指数估值提醒｜买卖信号&desp={msg}")

print("✅ 国内指数估值更新完成")

