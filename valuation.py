import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import akshare as ak

# ==========================================
# 1. 使用 AKShare 获取真实数据
# ==========================================
print("正在从 AKShare 获取真实行业数据，请稍候...")

# 定义我们要分析的真实板块（申万一级行业指数代码）
sectors = {
    '半导体': '801080',
    '银行': '801780',
    '食品饮料': '801120'
}

# 设定获取数据的时间范围（例如最近两年，保证估值百分位计算准确）
end_date = pd.Timestamp.today().strftime('%Y%m%d')
start_date = (pd.Timestamp.today() - pd.Timedelta(days=730)).strftime('%Y%m%d')

sectors_data = {}
valuation_status = pd.DataFrame()

for name, code in sectors.items():
    # 获取行业指数的历史行情（开高低收）
    df = ak.index_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date)
    if df.empty:
        continue
        
    # 数据清洗与重命名
    df.rename(columns={'日期':'Date', '开盘':'Open', '最高':'High', '最低':'Low', '收盘':'Close'}, inplace=True)
    df.set_index('Date', inplace=True)
    df.index = pd.to_datetime(df.index)
    sectors_data[name] = df
    
    # 获取该行业指数的历史市盈率(PE)数据
    try:
        pe_df = ak.index_value_hist_funddb(symbol=name, indicator="市盈率")
        pe_df.rename(columns={'日期':'Date'}, inplace=True)
        pe_df.set_index('Date', inplace=True)
        pe_df.index = pd.to_datetime(pe_df.index)
        
        # 计算PE的历史百分位（估值温度）：大于70%视为高估，小于30%视为低估
        pe_df['percentile'] = pe_df['市盈率'].rank(pct=True) * 100
        pe_df['status'] = pe_df['percentile'].apply(lambda x: '高估' if x > 70 else ('低估' if x < 30 else '正常'))
        
        valuation_status[name] = pe_df['status']
    except:
        print(f"警告：未能获取 {name} 的估值数据，将跳过该板块的估值背景绘制。")

# 对齐所有数据的日期索引
if not valuation_status.empty:
    common_dates = valuation_status.dropna(how='all').index
    valuation_status = valuation_status.loc[common_dates]
    for name in sectors_data:
        sectors_data[name] = sectors_data[name].loc[common_dates]

    # ==========================================
    # 2. 统计每天高估和低估的板块数量
    # ==========================================
    overvalued_count = (valuation_status == '高估').sum(axis=1)
    undervalued_count = (valuation_status == '低估').sum(axis=1)

    stats_df = pd.DataFrame({
        '高估板块数量': overvalued_count,
        '低估板块数量': undervalued_count
    })

    print("\n--- 📊 每日高低估值板块数量统计（最近10天） ---")
    print(stats_df.tail(10))
    print("\n")

    # ==========================================
    # 3. 使用 Plotly 绘制带真实估值背景色的交互式K线图
    # ==========================================
    target_sector = '半导体'
    if target_sector in sectors_data:
        df = sectors_data[target_sector]
        
        # 创建包含主图(K线)和副图(成交量)的画布
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, row_heights=[0.7, 0.3],
                            subplot_titles=(f'{target_sector} 真实K线与估值区间', '成交量'))

        # 绘制K线图
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name='K线', increasing_line_color='red', decreasing_line_color='green'
        ), row=1, col=1)

        # 绘制成交量柱状图
        colors = ['red' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'green' for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='成交量', marker_color=colors), row=2, col=1)

        # 遍历每一天，在背景上绘制真实的估值色块
        for i in range(len(valuation_status)):
            current_date = valuation_status.index[i]
            status = valuation_status.iloc[i][target_sector]
            
            if status == '高估':
                color = 'rgba(255, 100, 100, 0.2)' # 浅红色半透明
            elif status == '低估':
                color = 'rgba(100, 255, 100, 0.2)' # 浅绿色半透明
            else:
                continue # 正常估值不画背景
                
            # 在K线图和成交量图上都添加背景色块
            fig.add_vrect(x0=current_date, x1=current_date + pd.Timedelta(days=1), 
                          fillcolor=color, layer="below", line_width=0, row=1, col=1)
            fig.add_vrect(x0=current_date, x1=current_date + pd.Timedelta(days=1), 
                          fillcolor=color, layer="below", line_width=0, row=2, col=1)

        # 优化图表布局
        fig.update_layout(
            xaxis_rangeslider_visible=False, # 隐藏默认的范围滑块
            height=800,
            title_x=0.5,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_yaxes(title_text="价格", row=1, col=1)
        fig.update_yaxes(title_text="成交量", row=2, col=1)

        # 将图表保存为 HTML 文件，方便在 GitHub 网页中直接打开预览
        fig.write_html("valuation_chart.html")
        print("✅ 图表已成功生成！请在左侧文件栏点击打开 valuation_chart.html 查看交互式图表。")
else:
    print("❌ 未能获取到有效数据，请检查网络或稍后重试。")
