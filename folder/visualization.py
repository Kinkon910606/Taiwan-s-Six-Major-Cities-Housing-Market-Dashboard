import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import plotly.io as pio
pio.templates.default = "streamlit"


def lastly_month_average(data,type=1):
    
    # 三環折價率
    if type == 1:
        ym, unit, saleday, city = '交易年月', '合併單價', '銷售天期', '縣市'
    # 三環開價
    elif type == 2:
        ym, unit, saleday, city = 'ym', 'unit', 'saledays', 'city'
    
    elif type == 3:
        ym, unit, city = '交易年月', '合併單價', '縣市'

    ym_sort = np.sort(data[ym].unique())
    latest_month = ym_sort[-1]
    previous_month = ym_sort[-2]
    # print(np.sort(data[ym].unique()))
    # print(latest_month,previous_month)
    

    # 計算最後一個月平均成交單價與漲幅
    avg_price_last_month = data[data[ym] == latest_month][unit].mean()
    avg_price_prev_month = data[data[ym] == previous_month][unit].mean()
    price_change = ((avg_price_last_month - avg_price_prev_month) / avg_price_prev_month) * 100.
    # print(avg_price_last_month,avg_price_prev_month)

    # 計算最後一個月流通件數與漲幅
    count_last_month = data[data[ym] == latest_month][city].count()
    count_prev_month = data[data[ym] == previous_month][city].count()
    count_change = ((count_last_month - count_prev_month) / count_prev_month) * 100
    # print(count_last_month,count_prev_month)

    # 計算最後一個月平均銷售天期與漲幅
    if type == 3:
        return avg_price_last_month, count_last_month, price_change, count_change
    else:
        avg_saleday_last_month = data[data[ym] == latest_month][saleday].mean()
        avg_saleday_prev_month = data[data[ym] == previous_month][saleday].mean()
        saleday_change = ((avg_saleday_last_month - avg_saleday_prev_month) / avg_saleday_prev_month) * 100
        return avg_price_last_month, avg_saleday_last_month, count_last_month, price_change, saleday_change, count_change


    


import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
def create_monthly_chart(df, line_color, bar_color):
    """Create monthly combination chart"""
    df['交易年月'] = pd.to_datetime(df['交易年月'], format='%Y%m')
    
    # 計算每月平均單價和交易筆數
    monthly_data = df.groupby('交易年月').agg({
                '合併單價': 'mean',
                '交易年月': 'count'
            }).rename(columns={'交易年月': '交易筆數'}).reset_index()
   
    monthly_data.columns = ['交易年月', '平均單價', '交易筆數']
    monthly_data = monthly_data[-13:]
 
    # 建立組合圖
    fig = make_subplots(specs=[[{"secondary_y": True}]])
   
    # 添加折線圖 - 平均單價
    fig.add_trace(
        go.Scatter(
            x=monthly_data['交易年月'],
            y=monthly_data['平均單價'],
            name="平均單價",
            line=dict(color=line_color)
        ),
        secondary_y=True,
    )
   
    # 添加柱狀圖 - 交易筆數
    fig.add_trace(
        go.Bar(
            x=monthly_data['交易年月'],
            y=monthly_data['交易筆數'],
            name="交易筆數",
            marker_color=bar_color
        ),
        secondary_y=False,
    )
   
    # 更新布局
    fig.update_layout(
        title="月度交易分析",
        xaxis_title="交易年月",
        barmode='group',
        height=500
    )
   
    # 更新y軸標題
    fig.update_yaxes(title_text="交易筆數", secondary_y=False)
    fig.update_yaxes(title_text="平均單價", secondary_y=True)
   
    return fig

def create_quarterly_chart(df, line_color, bar_color):
    """Create quarterly combination chart"""
   
    
    # 計算每季平均單價和交易筆數
    quarterly_data = df.groupby('交易季').agg({
                '合併單價': 'mean',
                '交易年月': 'count'
            }).rename(columns={'交易年月': '交易筆數'}).reset_index()
    quarterly_data.columns = ['交易季', '平均單價', '交易筆數']
    
    # 建立組合圖
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 添加折線圖 - 平均單價
    fig.add_trace(
        go.Scatter(
            x=quarterly_data['交易季'],
            y=quarterly_data['平均單價'],
            name="平均單價",
            line=dict(color=line_color)
        ),
        secondary_y=True,
    )
    
    # 添加柱狀圖 - 交易筆數
    fig.add_trace(
        go.Bar(
            x=quarterly_data['交易季'],
            y=quarterly_data['交易筆數'],
            name="交易筆數",
            marker_color=bar_color
        ),
        secondary_y=False,
    )
    
    # 更新布局
    fig.update_layout(
        title="季度交易分析",
        xaxis_title="交易季",
        barmode='group',
        height=500
    )
    
    # 更新y軸標題
    fig.update_yaxes(title_text="交易筆數", secondary_y=False)
    fig.update_yaxes(title_text="平均單價", secondary_y=True)
    
    return fig

def community_counts(df):
    community_counts = df['社區名稱'].value_counts()
    top_10_communities = community_counts.head(10).reset_index()
    top_10_communities.columns = ['社區名稱', 'Count']
    fig = px.bar(top_10_communities, x='社區名稱', y='Count', color_discrete_sequence=['#D1B09C'])
    fig.update_layout(xaxis_tickangle=-45)
    return top_10_communities,fig

def page2_people(sorted_people):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # # 添加堆叠柱状图（男生和女生人口）
    # fig.add_trace(
    #     go.Bar(x=sorted_people['年月'], y=sorted_people['人口總數'], name='人口總數', marker_color='#041552', opacity=0.5),
    #     secondary_y=False
    # )

    # 添加折线图（人口成长率）
    fig.add_trace(
        go.Scatter(x=sorted_people['年月'], y=sorted_people['人口總數成長率'], name='人口月增率', mode='lines+markers', 
                line=dict(color='#B78969', width=2), marker=dict(size=8)),
        secondary_y=True
    )

    # 更新布局
    fig.update_layout(
        title='人口月增率趨勢圖',
        xaxis_title='年月',
        barmode='stack',  # 堆叠柱状图
        legend_title='圖例',
        hovermode='x unified'  # 鼠标悬停时显示所有系列的信息
    )

    # 为两个Y轴设置标题
    fig.update_yaxes(title_text="人口數", secondary_y=False)
    fig.update_yaxes(title_text="人口月增率 (%)", secondary_y=True)
    return fig

def page2_license(df):
        
    # 創建圖表
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['年月'], 
        y=df['建照住宅數'], 
        mode='lines+markers', 
        name='建照住宅數', 
        line=dict(color='#B78969', width=2),
        marker=dict(size=8, color='#B78969')
    ))

    fig.add_trace(go.Scatter(
        x=df['年月'], 
        y=df['使照住宅數'], 
        mode='lines+markers', 
        name='使照住宅數', 
        line=dict(color='#637C84', width=2),
        marker=dict(size=8, color='#637C84')
    ))

    # 更新佈局
    fig.update_layout(
        title='建使照趨勢',
        xaxis_title='年月',
        yaxis_title='建使照',
        hovermode='x unified'
    )
    return fig

def page2_buildings(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=df['年月'], y=df['移轉登記買賣棟數'], name='買賣棟數', marker_color='#D1B09C', opacity=0.5),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=df['年月'], y=df['移轉棟數成長率'], name='移轉棟數月增率', mode='lines+markers', 
                line=dict(color='#B78969', width=2), marker=dict(size=8)),
        secondary_y=True
    )

    fig.update_layout(
        title='移轉棟數趨勢圖',
        xaxis_title='年月',
        yaxis_title='移轉棟數',
        hovermode='x unified'
    )
    return fig

def page2_agent(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=df['年月'], y=df['件數'], name='流通件數', marker_color='#D1B09C', opacity=0.5),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=df['年月'], y=round(df['平均單價'],2), name='平均單價', mode='lines+markers', 
                line=dict(color='#B78969', width=2), marker=dict(size=8)),
        secondary_y=True
    )

    fig.update_layout(
        title='開價趨勢圖',
        xaxis_title='年月',
        yaxis_title='開價單價',
        hovermode='x unified'
    )
    return fig



def page2_sale(df,col):
    # 創建子圖
    if col =='交易年月':
        df[col] = df[col].astype(str)
        
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 添加平均單價折線（左側Y軸）
    fig.add_trace(
        go.Scatter(
            x=df[col], 
            y=df['平均成交單價'], 
            mode='lines+markers', 
            name='平均成交單價', 
            line=dict(color='#B78969', width=2),
            marker=dict(size=8, color='#B78969')
        ), 
        secondary_y=False
    )

    # 添加平均單價折線（左側Y軸）
    fig.add_trace(
    go.Scatter(
        x=df[col], 
        y=df['平均開價單價'], 
        mode='lines+markers', 
        name='平均開價單價', 
        line=dict(color='#D1B09C', width=2),
        marker=dict(size=8, color='#D1B09C')
    ), 
    secondary_y=False
    )

    # 添加平均折價率折線（右側Y軸）
    fig.add_trace(
        go.Bar(x=df[col], y=df['平均折價率'], name='平均折價率', marker_color='gray', opacity=0.5),
        secondary_y=True
    )

    # 更新佈局
    fig.update_layout(
        title='成交折價趨勢',
        xaxis_title=col,
        hovermode='x unified'
    )
    
    # 設置兩個Y軸的標題
    fig.update_yaxes(title_text="平均單價", secondary_y=False)
    fig.update_yaxes(title_text="平均折價率", secondary_y=True)
    return fig


def page2_saledays(df,col):
    if col =='交易年月':
        df[col] = df[col].astype(str)
        # df2[col] = df2[col].astype(str)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 添加平均單價折線（左側Y軸）
    fig.add_trace(go.Scatter(
            x=df[col], 
            y=df['銷售天期'], 
            mode='lines+markers', 
            name='平均銷售天期', 
            line=dict(color='#B78969', width=2),
            marker=dict(size=8, color='#B78969')))
    fig.update_layout(
        title='銷售天期趨勢',
        xaxis_title=col,
        hovermode='x unified'
    )

    fig.add_trace(
    go.Scatter(
        x=df[col], 
        y=df['平均開價單價'], 
        mode='lines+markers', 
        name='平均開價單價', 
        line=dict(color='#D1B09C', width=2),
        marker=dict(size=8, color='#D1B09C')
    ), 
    secondary_y=True,
    )
    return fig

# Treemap
def treemap_plot(visual_df):
    # 使用plotly建立互動式樹狀圖
    visual_df.loc[visual_df['宅數'] == 0, '宅數'] = 0.0001
    fig = px.treemap(
        visual_df,
        path=['區'],  # 設定層級路徑
        values='宅數',  # 使用宅數決定方塊大小
        title='各區宅數分布圖',
        custom_data=['宅數'],  # 設定懸停時顯示的資料
        color='宅數',
        color_continuous_scale='earth'
    )

    # 自訂圖表樣式
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>宅數: %{customdata[0]:,.0f}戶<extra></extra>",
        textinfo="label"
    )

    # 更新版面配置
    fig.update_layout(
        # 添加註解
        annotations=[
            dict(
                text="註：圖塊大小依宅數比例顯示",
                xref="paper",
                yref="paper",
                x=0.98,
                y=-0.05,
                showarrow=False,
                font=dict(size=10),
                align="right"
            )
        ]
    )
    return fig

# 低度用電趨勢圖
def Low_electricity_plot(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(go.Bar(
        x=df['年度'],
        y=df['宅數'],
        name='宅數',
        marker_color='#D1B09C',
        opacity=0.5),
        secondary_y=False)
    
    fig.add_trace(go.Scatter(
        x=df['年度'],
        y=df['比率'],
        mode='lines+markers',
        name='比率',
        line=dict(color='#B78969', width=2),
        marker=dict(size=8, color='#B78969')),
        secondary_y=True)
    
    # 更新佈局
    fig.update_layout(
        title='歷年低度用電趨勢',
        xaxis_title='季度',
        yaxis_title='宅數',
        hovermode='x unified'
    )
    
    return fig

# 待售新成屋趨勢圖
def newHouse_plot(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(go.Bar(
        x=df['YQ'],
        y=df['宅數'],
        name='宅數',
        marker_color='#D1B09C',
        opacity=0.5),
        secondary_y=False)
    
    # 更新佈局
    fig.update_layout(
        title='歷年待售新成屋趨勢',
        xaxis_title='年份季度',
        yaxis_title='宅數',
        hovermode='x unified'
    )
    
    return fig


# 八都成交趨勢
def Eight_city_plot(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
 
    fig.add_trace(go.Scatter(
        x=df['交易年月'],
        y=df['平均單價'],
        mode='lines+markers',
        name='平均單價',
        line=dict(color='#B78969', width=2),
        marker=dict(size=8, color='#B78969')),
        secondary_y=False)
    
    # 更新佈局
    fig.update_layout(
       
        xaxis_title='交易年月',
        yaxis_title='平均單價',
        hovermode='x unified'
    )
    
    return fig

#八都成交Treemap
def treemap8_plot(visual_df):
    # 使用plotly建立互動式樹狀圖
    visual_df.loc[visual_df['宅數'] == 0, '宅數'] = 0.0001
    fig = px.treemap(
        visual_df,
        path=['區'],  # 設定層級路徑
        values='宅數',  # 使用宅數決定方塊大小
       
        custom_data=['宅數'],  # 設定懸停時顯示的資料
        color='宅數',
        color_continuous_scale='earth'
    )

    # 自訂圖表樣式
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>宅數: %{customdata[0]:,.0f}戶<extra></extra>",
        textinfo="label"
    )

    # 更新版面配置
    fig.update_layout(
        # 添加註解
        annotations=[
            dict(
                text="註：圖塊大小依宅數比例顯示",
                xref="paper",
                yref="paper",
                x=0.98,
                y=-0.05,
                showarrow=False,
                font=dict(size=10),
                align="right"
            )
        ]
    )
    return fig

def Candlestick(df,city):
    df['變化率'] = (df['次月平均'] - df['本月平均']) / df['本月平均'] * 100
    # 創建雙軸圖表
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    down = df[df['PriceTrend'] == 'Down']

    # 主軸：金額趨勢
    fig.add_trace(
        go.Scatter(x=down['季'], y=down['變化率'], mode='lines+markers', 
                name='下跌變化率', line=dict(color='#B78969', width=2)),
        secondary_y=False
    )

    # 佈局設定
    fig.update_layout(
    #     title='季度金額與變化率分析',
        template='plotly_white',
        legend=dict(
        orientation="h",  # 水平排列
        yanchor="top",
        y=-0.2,          # 調整到圖表下方
        xanchor="center",
        x=0.5  ))

    # 軸標題
    # fig.update_yaxes(title_text="上漲變化率(%)", secondary_y=True)
    fig.update_yaxes(title_text="下跌變化率(%)", secondary_y=False) #, range=[0, max(down['變化率'])+5]

    return fig

def cheapenTreemap(data):
    data['city'] = data['city'].astype(str)
    data['dist'] = data['dist'].astype(str)

    # 創建完整的區域標籤 (城市-區域)
    data['full_label'] = data['city'] + '-' + data['dist']

    city_totals = data.groupby('city')['y'].sum().reset_index()
    city_totals.columns = ['city', 'city_total']

    # 合併總數到原始資料
    data = data.merge(city_totals, on='city')
    fig = px.treemap(
        data,
        path=['city', 'dist'],  # 定義層次結構
        values='y',             # 使用'y'列作為數值
        color='y',              # 使用'y'列作為顏色映射
        color_continuous_scale='earth',  # 使用藍色漸變色彩
        title='台灣城市區域分布Treemap',
        hover_data={'y': ':.0f', 'city_total': ':.0f'},  # 確保數值顯示為整數
        custom_data=['y', 'city_total']
    )

    # 自定義懸停文本格式
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>平均件數: %{customdata[0]}<br>城市總數: %{customdata[1]}<extra></extra>'
    )

    # 更新佈局
    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(family="Arial", size=14),
        coloraxis_colorbar=dict(
            title="數值",
            tickmode="array"
        )
    )
    return fig

#六都監控-折價天期線圖
def saledayPlot(df,l1,l2):
    # 創建雙軸圖表
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 主軸：金額趨勢
    fig.add_trace(
        go.Scatter(x=df['成交年月'], y=df[l1], mode='lines+markers', 
                name=l1, line=dict(color='#B78969', width=2)),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=df['成交年月'], y=df[l2], mode='lines+markers', 
                name=l2, line=dict(color='#D1B09C', width=2)),
        secondary_y=True
    )
   # 佈局設定
    fig.update_layout(
        template='plotly_white',
        legend=dict(
        orientation="h",  # 水平排列
        yanchor="top",
        y=-0.2,          # 調整到圖表下方
        xanchor="center",
        x=0.5 ,))

    # 軸標題
    fig.update_yaxes(title_text=l2, secondary_y=True)
    fig.update_yaxes(title_text=l1, secondary_y=False)
    return fig

#六都監控-單價線圖
def unitsPlot(df,l1,l2=None,l3= None, color1='#B78969', color2='#637C84', color3='#949871', xAxis='交易季'):
    # 創建雙軸圖表
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 主軸：金額趨勢
    fig.add_trace(
         go.Scatter(
            x=df[xAxis], 
            y=df[l1], 
            mode='lines+markers+text',
            name=l1, 
            line=dict(color=color1, width=2),
            text=df[l1],  # 顯示數值
            textfont=dict(size=14, color=color1),
            textposition='bottom center'  # 數值顯示位置
        ),
        secondary_y=False
    )
    if l2 is not None:
        fig.add_trace(
            go.Scatter(
                x=df[xAxis], 
                y=df[l2], 
                mode='lines+markers+text',
                name=l2, 
                line=dict(color=color2, width=2),
                text=df[l2],  # 顯示數值
                textfont=dict(size=14, color=color2),
                textposition='top center'  # 數值顯示位置
            ),
            secondary_y=False
        )
    if l3 is not None:
        fig.add_trace(
            go.Scatter(
                x=df[xAxis], 
                y=df[l3], 
                mode='lines+markers+text',
                name=l3, 
                line=dict(color=color3, width=3, dash='dashdot'),  # Changed color to forest green and made line dashed
                text=df[l3],  # 顯示數值
                textfont=dict(size=14, color=color3),
                textposition='top center'  # 數值顯示位置
            ),
            secondary_y=True
        )
   # 佈局設定
    fig.update_layout(
        template='plotly_white',
        legend=dict(
        orientation="h",  # 水平排列
        # yanchor="top",
        # y=-0.2,          # 調整到圖表下方
        xanchor="center",
        x=0.5 ,
        ))
    
     # 軸標題
    fig.update_yaxes(title_text=l3, secondary_y=True)
    fig.update_yaxes(title_text=l1, secondary_y=False)
    return fig


def unitsPlot2(df,l1,l2):
    # 創建雙軸圖表
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 主軸：金額趨勢
    fig.add_trace(
         go.Scatter(
            x=df['季'], 
            y=df[l1], 
            mode='lines+markers+text',
            name=l1, 
            line=dict(color='#B78969', width=2),
            text=df[l1],  # 顯示數值
            textposition='top center'  # 數值顯示位置
        ),
        secondary_y=False
    )

    fig.add_trace(
         go.Scatter(
            x=df['交易季'], 
            y=df[l2], 
            mode='lines+markers+text',
            name=l2, 
            line=dict(color='#D1B09C', width=2),
            text=df[l2],  # 顯示數值
            textposition='bottom center'  # 數值顯示位置
        ),
        secondary_y=True
    )
   # 佈局設定
    fig.update_layout(
        template='plotly_white',
        legend=dict(
        orientation="h",  # 水平排列
        xanchor="center",
        x=0.5 ,
        ))

    # 軸標題
    fig.update_yaxes(title_text=l2, secondary_y=True)
    fig.update_yaxes(title_text=l1, secondary_y=False)
    return fig

def unitsPlot3(df, l1, l2, xAxis='交易季', color1='#637C84', color2='#000000'):
    # 創建雙軸圖表
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # THEN add the bar chart second so it appears on top
    fig.add_trace(
        go.Scatter(
            x=df[xAxis], 
            y=df[l1], 
            mode='lines+markers+text',
            name=l1, 
            line=dict(color=color2, width=2),
            text=df[l1],  # 顯示數值
            textposition='top center',  # 數值顯示位置
            textfont=dict(size=14,color=color2)  # 設定數值顏色為黑色
        ),
        secondary_y=False
    )
    
    # 主軸：金額趨勢 (Add scatter plot FIRST)
    fig.add_trace(
        go.Bar(
            x=df[xAxis], 
            y=df[l2], 
            name=l2, 
            marker_color=color1,
            text=[f'{val:,.0f}' for val in df[l2]],  # 顯示數值並新增千分位符號
            textfont=dict(size=14, color='white'),
            opacity=0.7
        ),
        secondary_y=True
    )

    # 佈局設定
    fig.update_layout(
        template='plotly_white',
        legend=dict(
            orientation="h",  # 水平排列
            xanchor="center",
            x=0.5
        )
    )

    # 軸標題
    fig.update_yaxes(title_text=l1, secondary_y=False)
    fig.update_yaxes(title_text=l2, secondary_y=True)
    return fig

def unitsPlot4(df, l1, l2, l3, xAxis = '鄉鎮市區',
               color1='#D1B09C', color2='#B78969', color3='#949871'):
    # 創建雙軸圖表
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 添加直條圖 - l1
    fig.add_trace(
        go.Bar(
            x=df[xAxis], 
            y=df[l1], 
            name=l1, 
            marker_color=color1, 
            text=df[l1],  # 顯示數值
            textfont=dict(size=14, color='black'),
            opacity=0.7
        ),
        secondary_y=False
    )

    # 添加直條圖 - l2
    fig.add_trace(
        go.Bar(
            x=df[xAxis], 
            y=df[l2], 
            name=l2, 
            marker_color=color2, 
            text=df[l2],  # 顯示數值
            textfont=dict(size=14, color='white'),
            opacity=0.7
        ),
        secondary_y=False
    )

    # 添加摺線圖 - l3
    fig.add_trace(
        go.Scatter(
            x=df[xAxis], 
            y=df[l3], 
            mode='markers+text', 
            name=l3, 
            line=dict(color=color3, width=2),
            text=df[l3],  # 顯示數值
            textposition='bottom center',
            marker=dict(size=12, color=color3),
            textfont=dict(size=14, color=color3)  # Set text font size and color
        ),
        secondary_y=True
    )

    # 更新佈局
    fig.update_layout(
        # title='鄉鎮市區平均銷售天期與成長率',
        # xaxis_title='鄉鎮市區',
        barmode='group',  # 分組直條圖
        template='plotly_white',
        legend=dict(
            orientation="h",  # 水平排列
            xanchor="center",
            x=0.5
        )
    )

    # 設置Y軸標題
    fig.update_yaxes(title_text="平均銷售天期", secondary_y=False)
    fig.update_yaxes(title_text="增加率 (%)", secondary_y=True)

    return fig
def monitorTreemap(data, column , path = ['縣市', '鄉鎮市區']):
    # 確保城市和區域名稱為字符串類型
    data[path] = data[path].astype(str)
    # data['鄉  鎮市區'] = data['鄉鎮市區'].astype(str)
    data[column] = pd.to_numeric(data[column], errors='coerce').astype(float)
    # 處理零值
    data.loc[data[column] == 0, column] = 0.0001
    
    # 創建Treemap
    fig = px.treemap(
        data,
        path=path,  # 設定層級路徑：縣市 -> 鄉鎮市區
        values=column,               # 使用數值列作為數值
        color=column,                # 使用數值列作為顏色映射
        color_continuous_scale='earth',  # 使用漸變色彩
        hover_data=[column],
        custom_data=[column]
    )

    # 自定義懸停文本格式
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>數值: %{customdata[0]}<extra></extra>',
        textinfo="label"  # 確保標籤顯示
    )

    # 更新佈局
    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(family="Arial", size=14),
        coloraxis_colorbar=dict(
            title="數值",
            tickmode="array"
        )
    )

    return fig
