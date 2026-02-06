import pymssql
import pandas as pd

"""
這裡的SQL語法都會直接接到\\10.11.6.12\r41200\M07927(亭妤)\LibreChat\LibreChat代理模型\code底下的sql檔案
- \\10.11.6.12\r41200\M07927(亭妤)\LibreChat\LibreChat代理模型\code\縣市(季).sql
- \\10.11.6.12\r41200\M07927(亭妤)\Streamlit儀錶板\folder\saledays.sql
"""

def select_data(conn, sql_path):
    cursor = conn.cursor()
    
    # sql_path = r'\\10.11.6.12\r41200\M07927(亭妤)\Streamlit儀錶板\folder\saledays.sql'
    with open(sql_path, 'r') as f:
        SQL_QUERY = f.read() # 讀取整個檔案內容

    cursor.execute(SQL_QUERY)
    data=cursor.fetchall()
    df=pd.DataFrame(data)

    conn.commit()
    cursor.close()

    return df