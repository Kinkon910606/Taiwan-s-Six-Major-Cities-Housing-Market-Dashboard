import streamlit as st
import pandas as pd
import time
from datetime import datetime,timedelta
today = datetime.now()
from folder.SQL_query import *
from folder.visualization import *
import openai

st.logo(r'https://bank.sinopac.com/sinopacbt/webevents/2005_life/images/logo@3x.png', size='large')

# API 設定
openai.api_key = "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"  # 替換成您的 API Key
openai.api_base = "https://api.groq.com/openai/v1"

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
def load_data(): #讀取資料
    # df = select_data(st.session_state.db_connection, 
    #     r".\sql\agent_data.sql")
    # df2 = select_data(st.session_state.db_connection,
    #     r".\sql\saledays_month.sql")
    df = pd.read_csv(r'./data/agent_data.csv', encoding='utf-8')
    df2 = pd.read_csv(r'./data/saledays_month.csv', encoding='utf-8')
    return df, df2

################################################################################
#主程式
def main():
    
    
    
    if st.session_state.data_loaded_3 == False:
        st.toast("請稍候，資料載入需要下載1~5分鐘")
        st.session_state.data_2, st.session_state.saleday_2 = load_data()
        st.session_state.data_loaded_3 = True
    
    if st.session_state.data_loaded_3 == True:
        b1, b2, b3, empty = st.columns([1,1,1,1])
        with b1:
            city = st.selectbox('縣市',st.session_state.data_2['縣市'].unique())
            data = st.session_state.data_2[st.session_state.data_2['縣市']==city]
        
            saleday = st.session_state.saleday_2[st.session_state.saleday_2['縣市']==city]
            saleday['年月'] = pd.to_datetime(saleday['年月'], format='%Y%m')

        with b2:
            start_ym = st.selectbox("開始年月", data['年月'].unique().astype(int), index = len(data['年月'].unique())-13)
        with b3:
            end_list = [int(x) for x in data['年月'].unique() if int(x) > int(start_ym)]
            end_ym = st.selectbox("結束年月", end_list, index = len(end_list)-1)

        data = data[(data['年月'] >= start_ym) & (data['年月'] <= end_ym)]
        data['年月'] = pd.to_datetime(data['年月'], format='%Y%m')
        data = data.sort_values(by='年月')
        data['年月'] = data['年月'].dt.strftime('%Y%m')

        # st.markdown(end_list)
        st.subheader('Data Table',divider=True )
        if st.toggle('切換資料表'):
            st.caption('資料來源: 公開售屋平台開價資訊。 ※計算當月與前月成長幅度')
            st.dataframe(saleday)
        else:
            st.caption('資料來源: 公開售屋平台開價資訊。 ※計算每月各類指標平均值及總計')
            st.dataframe(data)


        bc1,bc2 = st.columns(2)
        with bc1:
            title, col1 = st.columns([10,1],vertical_alignment='bottom')

            color1 = col1.color_picker("銷售單價(萬/坪)", "#b78969",key='color1_data1',label_visibility='hidden')

            title.subheader('開價單價  :chart_with_upwards_trend: ',divider=True,anchor=False)
            st.plotly_chart(unitsPlot(df = data,
                                      l1 = '銷售單價(萬/坪)',
                                    #   l2 = '流動天期(天)',
                                      color1 = color1,
                                    #   color2 = color2,
                                      xAxis='年月'))

        with bc2:
            title, col1, col2 = st.columns([9,1,1],vertical_alignment='bottom')

            color1 = col1.color_picker("銷售單價(萬/坪)", "#637C84",key='color1_data2',label_visibility='hidden')
            color2 = col2.color_picker("流動天期(天)", "#000000",key='color2_data2',label_visibility='hidden')

            title.subheader('流動天期 :bar_chart: ',divider=True ,anchor=False)
            st.plotly_chart(unitsPlot3(df = data,
                                       l1 = '流動天期(天)',
                                       l2 = '流動量(棟)',
                                       color1 = color1,
                                       color2 = color2,
                                       xAxis='年月'))
            
        
        # bc1,bc2 = st.columns(2,vertical_alignment='bottom')
        st.subheader(f'{saleday["年月"].max().year}年{saleday["年月"].max().month}月流動天期樹狀圖 :bar_chart: ',divider=True,anchor=False)
        # with bc2:
        #     title, col1, col2, col3 = st.columns([8,1,1,1],vertical_alignment='bottom')

        #     title.subheader('流通天期增加率:wrench: ',divider=True ,anchor=False)
        #     # col1, col2, col3 = st.columns(3)
        #     color1 = col1.color_picker("前季銷售天期", "#d1b09c", key='color1_data3',label_visibility='hidden')
        #     color2 = col2.color_picker("當季銷售天期", "#b78969", key='color2_data3',label_visibility='hidden')
        #     color3 = col3.color_picker("增加率(%)", "#949871", key='color3_data3',label_visibility='hidden')

        # bc1,bc2 = st.columns(2,vertical_alignment='bottom')
        st.plotly_chart(monitorTreemap(saleday,'當月銷售天期',path = ['縣市', '行政區']))
        # bc2.plotly_chart(unitsPlot4(saleday,"前月銷售天期","當月銷售天期",'增加率(%)',xAxis='行政區',
        #                         color1=color1, color2=color2, color3=color3))

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
            # st.session_state.data_loaded_2 = False
            # st.session_state.data_loaded_3 = False
            # st.session_state.data_loaded_6 = False
            # st.session_state.data_dist = None
            # st.session_state.data, st.session_state.data2 = None, None
            # st.session_state.data_2, st.session_state.saleday_2  = None, None
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
