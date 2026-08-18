import streamlit as st
import pandas as pd
import time
from datetime import datetime,timedelta
today = datetime.now()
from folder.SQL_query import *
from folder.visualization import *
import os


st.logo(r'https://bank.sinopac.com/sinopacbt/webevents/2005_life/images/logo@3x.png', size='large')

st.set_page_config(
    page_title="永豐銀行-鑑估中心儀表板",
    page_icon="images/icon.png",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items = {
        "About": "author : Kuo"
    }
)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False 


################################################################################
###  讀取資料 ###
@st.cache_data
def load_data(): #- 讀取資料
    #- 正式版：直接串接資料庫，讀取資料
    # df = select_data(st.session_state.db_connection, 
    #                      r".\folder\縣市(季).sql")
    # df2 = select_data(st.session_state.db_connection,
    #                   r".\folder\saledays_quarter.sql")
    #- 測試版：讀取csv檔案
    df = pd.read_csv(r'./data/縣市(季).csv', encoding='utf-8')
    df2 = pd.read_csv(r'./data/saledays_quarter.csv', encoding='utf-8')
    return df, df2

@st.cache_data
def convert_for_download(df):
    return df.to_csv(index=False).encode("utf-8-sig")

def stream_generator(text: str, cps: float = 24): #- 控制打字速度，讓AI的回覆可以像打字機一樣逐字呈現
    delay = 1.0 / max(cps, 1)
    for ch in text:
        yield ch
        time.sleep(delay)

################################################################################
#主程式
def main():
    #- 判斷是否需要讀取資料。如果是第一次進入頁面，就會執行這一段，目的是為了只讀取一次資料。
    if st.session_state.data_loaded_2 == False:
        st.toast("請稍候，資料載入需要下載1~5分鐘")
        st.session_state.data, st.session_state.data2 = load_data()
        st.session_state.data_loaded_2 = True
    
    if st.session_state.data_loaded_2 == True:
        b1,b2,b3,download,btn = st.columns([1,1,1,1,1], vertical_alignment='bottom')
        cityList = st.session_state.data['縣市'].unique()
        # cityList.remove(None)
        city = b1.selectbox('縣市',cityList)
        
        data2 = st.session_state.data2[st.session_state.data2['縣市']==city]
        data2 = data2.sort_values(by='增加率(%)',ascending=False).reset_index(drop=True)

        yqList = st.session_state.data['交易季'].unique().tolist()
        start_yq = b2.selectbox('開始交易季',yqList, index=len(yqList)-5)
        end_yq = b3.selectbox('結束交易季',yqList[yqList.index(start_yq)+1:], index=len(yqList[yqList.index(start_yq)+1:])-1)

        data = st.session_state.data[(st.session_state.data['交易季']>=start_yq) & (st.session_state.data['交易季']<=end_yq)].reset_index(drop=True)
        data_ = data[data['縣市']==city]

        if btn.button('生成評析', width='stretch'):
            
            st.sidebar.caption("以下分析結果來源:LibreChat")
            st.sidebar.info("該評析並無串接GAI任何模型，僅為LibreChat的回覆結果，數據並無即時更新，評析內容僅供參考。")
            f = open(rf"{os.getcwd()}/prompt_and_responses/responses_{city}.txt", "r+")
            st.sidebar.write_stream(stream_generator(f.read(), cps = 800))  # cps:打字速度。數值越高，速度越快
        
        csv = convert_for_download(st.session_state.data)
        download.download_button(
                label="Download CSV",
                data=csv,
                file_name="六都開價追蹤_縣市_季.csv",
                mime="text/csv",
                icon=":material/download:",
                width='stretch'
            ) 
        
        st.subheader('Data Table',divider=True )
        if st.toggle("切換資料表"):
            st.caption('資料來源: 公開售屋平台開價資訊。 ※計算當季與前季成長幅度')
            st.dataframe(data2)  
        else:
            st.caption('資料來源: 公開售屋平台開價資訊、內政部實價登錄資訊、內政部買賣移轉棟數。 ※計算每季各類指標平均值及總計')

            st.dataframe(data_)
            


        bc1,bc2 = st.columns(2,vertical_alignment='bottom')
        with bc1:
            title, col1, col2,col3 = st.columns([8,1,1,1],vertical_alignment='bottom')
            
            title.subheader('開價、成交、議價率(%)折線圖 :chart_with_upwards_trend: ',divider=True,anchor=False)

            color1 = col1.color_picker("市場開價(萬/坪)", "#b78969",key='color1_data1',label_visibility='hidden')
            color2 = col2.color_picker("成交行情(萬/坪)", "#637c84",key='color2_data1',label_visibility='hidden')
            color3 = col3.color_picker("買賣議價率(%)", "#949871",key='color3_data12',label_visibility='hidden')
        with bc2:
            title, col1, col2 = st.columns([9,1,1],vertical_alignment='bottom')

            title.subheader('買賣移轉(棟)+銷售天期(天)折線圖 :bar_chart: ',divider=True,anchor=False)
            color1_ = col1.color_picker("交易量(棟)", "#637c84",key='color1_data2',label_visibility='hidden')
            color2_ = col2.color_picker("銷售天期(天)", "#000000",key='color2_data2',label_visibility='hidden')
            
        bc1,bc2 = st.columns(2)
        bc1.plotly_chart(unitsPlot(df = data_, l1 = '市場開價(萬/坪)', l2 = '成交行情(萬/坪)', l3 = '買賣議價率(%)',
                                    color1 = color1, color2 = color2, color3 = color3, xAxis='交易季'))
        bc2.plotly_chart(unitsPlot3(df = data_, l1 = '銷售天期(天)', l2 = '交易量(棟)', 
                                    color1 = color1_, color2 = color2_, xAxis='交易季'))
            
        bc1,bc2 = st.columns(2,vertical_alignment='bottom')
        bc1.subheader('當季銷售天期樹狀圖 :bar_chart: ',divider=True,anchor=False)
        bc2.subheader('全區比較折線圖 :chart_with_upwards_trend: ',divider=True,anchor=False)
        # with bc2:
        #     title, col1, col2,col3 = st.columns([8,1,1,1],vertical_alignment='bottom')
            
        #     title.subheader('銷售天期增加率:wrench: ',divider=True,anchor=False)
        #     # col1, col2,col3 = st.columns(3)
        #     color1 = col1.color_picker("前季銷售天期", "#d1b09c", key='color1_data3',label_visibility='hidden')
        #     color2 = col2.color_picker("當季銷售天期", "#b78969", key='color2_data3',label_visibility='hidden')
        #     color3 = col3.color_picker("增加率(%)", "#949871", key='color3_data3',label_visibility='hidden')

        bc1,bc2 = st.columns(2,vertical_alignment='top')
        bc1.plotly_chart(monitorTreemap(st.session_state.data2,'當季銷售天期'))
        with bc2:
            COLUMNS = st.pills(label='', options=st.session_state.data.columns[3:], label_visibility='hidden', default=st.session_state.data.columns[3])
            if COLUMNS:
                df_group = data.pivot(index='交易季',columns='縣市', values=COLUMNS).reset_index(drop=False)

                fig = go.Figure()

                cities = df_group.columns[1:]
                for city in cities:
                    fig.add_trace(go.Scatter(x=df_group['交易季'], 
                                             y=df_group[city], 
                                             mode='lines+markers+text', 
                                             name=city,
                                             text=df_group[city],
                                             textposition='top center',  # 數值顯示位置
                                             textfont=dict(size=14,color=color2) )) # 設定數值顏色為黑色

                fig.update_layout(
                    # title='六都季度變化折線圖',
                    xaxis_title='交易季',
                    yaxis_title=COLUMNS,
                    legend_title='縣市',
                    template='plotly_white'
                )
                st.plotly_chart(fig)
        # bc2.plotly_chart(unitsPlot4(data2,"前季銷售天期","當季銷售天期",'增加率(%)',
        #                                color1=color1, color2=color2, color3=color3))



        
################################################################################

#判斷登入狀態
try:
    if st.session_state.login_status: #"login_status" in st.session_state and 
        st.caption("您已登入，現在可以操作資料庫。")
        main()
        Logout = st.sidebar.button('登出')
        
        if Logout:
            st.toast("登出成功")
            st.session_state.login_status = False
            st.session_state.show_form = True
            st.session_state.data_loaded_2 = False
            st.session_state.data_loaded_6 = False
            st.session_state.data_dist = None
            st.session_state.data, st.session_state.data2 = None, None
            time.sleep(2)
            st.switch_page("main.py")

    else:
        st.error("尚未登入，請返回主頁登入。五秒後會自動跳回主頁！")
        time.sleep(5)
        st.switch_page("main.py")

except Exception as e:
    st.toast(f"登入失敗，{e}")
    time.sleep(5)
    st.switch_page("main.py")
