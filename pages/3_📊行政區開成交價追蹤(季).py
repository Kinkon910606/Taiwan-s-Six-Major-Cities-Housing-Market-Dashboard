import streamlit as st
import pandas as pd
import time
from datetime import datetime,timedelta
today = datetime.now()
from folder.SQL_query import *
from folder.visualization import *
import os
from groq import Groq

from pathlib import Path


def read_template(path: str, encoding: str = "utf-8") -> str:
    p = Path(path)
    text = p.read_text(encoding=encoding)
    return text

st.logo(r'https://bank.sinopac.com/sinopacbt/webevents/2005_life/images/logo@3x.png', size='large')
# API 設定
api_key = st.sidebar.text_input("請輸入你的Groq API Key", type="password", key="api_key_input")
st.sidebar.info("提醒：若無API Key，請先前往Groq官網申請\n https://console.groq.com/keys", icon="⚠️")

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
@st.cache_data

def load_data(): #- 讀取資料
    #- 正式版：直接串接資料庫，讀取資料
    # df = select_data(st.session_state.db_connection, 
    #                  r".\folder\鄉鎮市區(季).sql")
    #- 測試版：讀取csv檔案
    df = pd.read_csv(r'./data/鄉鎮市區(季).csv', encoding='utf-8')
    return df

@st.cache_data
def convert_for_download(df):
    return df.to_csv(index=False).encode("utf-8-sig")

def load_response(data, city, dist, type, endYQ, api_key): #- 獲取AI生成的結論
    ### 模型設定 ###
    client = Groq(api_key=api_key)  # 初始化 Groq 客戶端
    model = "openai/gpt-oss-20b"

    ### 讀取prompt_and_responses中的system_prompt.txt ###
    system_prompt  = read_template(rf"{os.getcwd()}/prompt_and_responses/system_prompt.txt").format(**{"endYQ":endYQ}) #讀取prompt_and_responses中的system_prompt.txt
    
    ### User_prompt ###
    final_prompt = f"""根據下列表格回答問題：{data}。請針對表格內的資訊對{city}{dist}中{type}進行資料分析"""

    try:
        # 呼叫生成式AI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": final_prompt},
            ],
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            reasoning_effort="medium",
            stream=True,
            stop=None
        )

        # 取得AI回答
        answer = ""
        for chunk in response:
            answer += chunk.choices[0].delta.content or ""  
        return answer
        
    except Exception as e: #! 執行錯誤，回報錯誤
        error_msg = f"生成回應時發生錯誤: {str(e)}"
        # print(error_msg)
        return error_msg

def stream_generator(text: str, cps: float = 24): #- 控制打字速度，讓AI的回覆可以像打字機一樣逐字呈現
    delay = 1.0 / max(cps, 1)
    for ch in text:
        yield ch
        time.sleep(delay)

################################################################################
#主程式
def main():
    
    #- 判斷是否需要讀取資料。如果是第一次進入頁面，就會執行這一段，目的是為了只讀取一次資料。
    if st.session_state.data_loaded_6 == False:
        st.toast("請稍候，資料載入需要下載1~5分鐘")
        st.session_state.data_dist = load_data()
        st.session_state.data_loaded_6 = True


    if st.session_state.data_loaded_6 == True:
        #- 選項區
        b1, b2, b3, b4, b5, download = st.columns(6, vertical_alignment='bottom')
        
        city = b1.selectbox('縣市',st.session_state.data_dist['縣市'].unique())
        data = st.session_state.data_dist[st.session_state.data_dist['縣市']==city]
        
        dist = b2.selectbox('行政區', data['行政區'].unique())
        data2 = data[data['行政區']==dist]
        
        type = b3.selectbox('建物類別', data2['建物類別名稱'].unique())
        data2 = data2[data2['建物類別名稱']==type]
        
        yqList = sorted(st.session_state.data_dist['交易季'].unique())[:-1]
        start_yq = b4.selectbox('開始交易季',yqList, index=len(yqList)-5)
        end_yq = b5.selectbox('結束交易季',yqList[yqList.index(start_yq)+1:], index=len(yqList[yqList.index(start_yq)+1:])-1)

        data2 = data2[(data2['交易季']>= start_yq) & (data2['交易季']<= end_yq)]
        endYQ = st.sidebar.selectbox("評析比較季", sorted(data2['交易季'].unique(), reverse=True))
        btn = st.sidebar.button('生成評析',width='stretch')
        data2 = data2.sort_values(by='交易季',ascending=True).reset_index(drop=True)

        csv = convert_for_download(st.session_state.data_dist)
        download.download_button(
                label="Download CSV",
                data=csv,
                file_name="六都開價追蹤_行政區_季.csv",
                mime="text/csv",
                icon=":material/download:",
                width='stretch'
            ) 
    
        #- 如果按下"生成評析"，就會產生AI評析結論:打字機動畫。
        if btn:
            st.sidebar.caption("以下分析結果來源:Groq")
            st.sidebar.write_stream(stream_generator(load_response(data2.to_dict(), city, dist, type, endYQ, api_key), cps = 500)) # cps:打字速度。數值越高，速度越快
            # st.sidebar.markdown()     

        #- 呈現資料表
        st.subheader('Data Table',divider=True,anchor=False)
        st.caption('資料來源: 公開售屋平台開價資訊、內政部實價登錄資訊。 ※計算每季各類指標平均值及總計')

        st.dataframe(data2)

        # #- 圖表區
        bc1,bc2 = st.columns(2)
        with bc1:
            title, col1, col2,col3 = st.columns([8,1,1,1],vertical_alignment='bottom')
            title.subheader('開價、成交、議價率(%)折線圖 :chart_with_upwards_trend: ',divider=True,anchor=False)

            # col1, col2,col3 = st.columns(3)
            color1 = col1.color_picker(" ", "#b78969",label_visibility='hidden')
            color2 = col2.color_picker(" ", "#637c84",label_visibility='hidden')
            color3 = col3.color_picker(" ", "#949871",label_visibility='hidden')
            
            st.plotly_chart(unitsPlot(df = data2,
                                      l1 = '市場開價(萬/坪)',
                                      l2 = '成交行情(萬/坪)',
                                      l3 = '買賣議價率(%)',
                                      color1 = color1,
                                      color2 = color2,
                                      color3 = color3,
                                      xAxis='交易季'))

        with bc2:
            title, col1, col2 = st.columns([9,1,1],vertical_alignment='bottom')
            title.subheader('買賣移轉(棟)+銷售天期(天)折線圖 :bar_chart: ',divider=True,anchor=False)

            # col1, col2, col3 = st.columns(3)
            color1_ = col1.color_picker(" ", "#637c84",key='color1_data2',label_visibility='hidden')
            color2_ = col2.color_picker(" ", "#000000",key='color2_data2',label_visibility='hidden')
            
            st.plotly_chart(unitsPlot3(df = data2,
                                       l1 = '銷售天期(天)',
                                       l2 = '交易量(棟)',
                                       color1 = color1_,
                                       color2 = color2_,
                                       xAxis='交易季'))
            
################################################################################

#判斷登入狀態
try:
    if st.session_state.login_status: #"login_status" in st.session_state and 
        # st.caption("您已登入，現在可以操作資料庫。")
        main()
        Logout = st.sidebar.button('登出')
        
        if Logout:
            st.toast("登出成功")
            st.session_state.login_status = False
            st.session_state.show_form = True
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
