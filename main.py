"""
streamlit run main.py --server.port 8510
streamlit run main.py --server.fileWatcherType poll
"""
import streamlit as st
import time
# import pymssql
from datetime import datetime, timedelta

# from sqlalchemy import create_engine


# 初始化 session_state
def initialize_state():
    # 功能性變數
    if "db_connection" not in st.session_state:
            st.session_state.db_connection = None
    if "login_status" not in st.session_state:
        st.session_state.login_status = False
    if 'disabled' not in st.session_state:
        st.session_state.disabled = False
    if 'start_year' not in st.session_state:
        st.session_state.start_year = datetime.now().year-1
    if 'start_month' not in st.session_state:
        st.session_state.start_month = 1
    if 'end_year' not in st.session_state:
        st.session_state.end_year = datetime.now().year
    if 'end_month' not in st.session_state:
        st.session_state.end_month = datetime.now().month
        
    # 資料載入狀態
    if 'data_loaded_2' not in st.session_state:
        st.session_state.data_loaded_2 = False
    if 'data_loaded_3' not in st.session_state:
        st.session_state.data_loaded_3 = False
    if 'data_loaded_6' not in st.session_state:
        st.session_state.data_loaded_6 = False
    if 'response' not in st.session_state:
        st.session_state.response = {}

# st.image("images/logo.png")
st.set_page_config(
    page_title="永豐銀行-鑑估中心儀表板",
    page_icon="images/icon.png",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items = {
        "About": "author : Kuo"
    }
)
# 文字說明
st.title("房價動態資訊Dashboard使用說明")

st.markdown('---')
st.write("""歡迎使用不動產儀表板！本儀表板提供您多方位的數據分析工具，幫助您快速掌握市場動態。""")

st.write(':pushpin: 提醒：使用前，請務必先登入您的 SQL Server 帳號，以獲取完整的數據支持。')
st.markdown('---')

# pages = {
#     "pages": [
#         st.Page("page_1.py", title="低度用電 & 待售新成屋"),
#         st.Page("page_2.py", title="總覽"),
#         st.Page("page_3.py", title="三環成交報告"),
#         st.Page("page_4.py", title="六都成交報告"),
#         st.Page("page_5.py", title="降價區資訊"),
#         st.Page("page_6.py", title="六都監控報告"),
#         st.Page("page_7.py", title="(空)"),
#         st.Page("page_8.py", title="狀態"),

#     ]
# }

# pg = st.navigation(pages)


# SQL Server 登入頁面

initialize_state()
if st.session_state.login_status == False:
    st.header("SQL Server Login")
    st.caption("立即登入並開始探索！")

    server = st.text_input("server:", value="10.11.144.102")
    database = st.text_input("Database Name:", value="DB_DIGITECH")
    user = st.text_input("Username:", value="104901")
    password = st.text_input("Password:", type="password", value="Aa@20260102")
    login = st.button("Enter :gear:")
    st.warning("此版本為測試版本，數據並不會即時更新，僅供測試使用。")

    if login:
        if server and database and user and password:
            try:
                # 模擬成功連線（正式版將會替換成實際的 SQL Server 驗證邏輯）
                # conn = pymssql.connect(
                #     server=f'{server}',
                #     user=f'{user}',
                #     password= f'{password}',
                #     database=f'{database}',
                #     as_dict=True,autocommit=True)
                
                st.session_state.login_status = True  # 更新登入狀態
                st.session_state.db_connection = "TRUE"
                

                st.switch_page("main.py")

            except Exception as e:
                st.error(f"登入失敗，請檢查輸入是否正確：{e}")
        else:
            st.error("請確實填寫所有欄位")

if st.session_state.login_status == True and st.session_state.db_connection is not None:
    st.toast("登入成功，歡迎使用系統！")
    
    Logout = st.sidebar.button('登出')
    if Logout:
        st.toast("登出成功")
        time.sleep(1)

        st.session_state.login_status = False
        # st.session_state.show_form = True
        st.switch_page("main.py")

