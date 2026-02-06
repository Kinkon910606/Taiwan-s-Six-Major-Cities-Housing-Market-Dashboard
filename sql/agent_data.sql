-- 主要改動說明:
-- 使用 INFORMATION_SCHEMA.TABLES 查詢所有 A_W 開頭的資料表
-- 動態產生 UNION ALL 語句
-- 在動態 SQL 中，所有單引號需要用兩個單引號 '' 來跳脫
-- 使用 sp_executesql 執行動態產生的 SQL


DECLARE @sql NVARCHAR(MAX) = '';

-- 動態產生 UNION ALL 語句
SELECT @sql = @sql + 
    'SELECT * FROM ' + QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) + ' UNION ALL '
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE 'A_W%'
ORDER BY TABLE_NAME;

-- 移除最後一個 UNION ALL
SET @sql = LEFT(@sql, LEN(@sql) - 10);

-- 組合完整的查詢
SET @sql = '
SELECT ym AS [年月],
       city AS [縣市],
       ROUND(AVG(unit), 1) AS [銷售單價(萬/坪)], 
       ROUND(AVG(saledays), 0) AS [流動天期(天)], 
       COUNT(*) AS [流動量(棟)]
FROM (' + @sql + ') cte
WHERE 
    (
        (city = ''台北市'' AND size BETWEEN 5 AND 400 AND unit BETWEEN 5 AND 400) OR
        (city = ''新竹縣'' AND size BETWEEN 5 AND 400 AND unit BETWEEN 5 AND 400) OR
        (city = ''新北市'' AND dist NOT IN (''萬里區'',''金山區'',''貢寮區'',''雙溪區'',''瑞芳區'',''平溪區'',''石碇區'',''坪林區'',''烏來區'',''三芝區'',''石門區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300) OR
        (city = ''桃園市'' AND dist NOT IN (''新屋區'',''觀音區'',''大溪區'',''復興區'',''龍潭區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300) OR
        (city = ''台中市'' AND dist NOT IN (''大甲區'',''大安區'',''外埔區'',''東勢區'',''和平區'',''清水區'',''石岡區'',''新社區'',''梧棲區'',''霧峰區'',''沙鹿區'',''大肚區'',''后里區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300) OR
        (city = ''台南市'' AND dist NOT IN (''七股區'',''下營區'',''六甲區'',''左鎮區'',''玉井區'',''白河區'',''西港區'',''安定區'',''官田區'',''東山區'',''南化區'',''後壁區'',''柳營區'',''麻豆區'',
                                        ''將軍區'',''楠西區'',''龍崎區'',''學甲區'',''關廟區'',''鹽水區'',''大內區'',''山上區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300) OR
        (city = ''高雄市'' AND dist NOT IN (''鳥松區'',''旗津區'',''大寮區'',''大社區'',''林園區'',''路竹區'',''燕巢區'',''梓官區'',''大樹區'',''六龜區'',''內門區'',''田寮區'',''永安區'',''甲仙區'',''杉林區'',
                                        ''阿蓮區'',''美濃區'',''桃源區'',''梓官區'',''茂林區'',''茄定區'',''茄萣區'',''湖內區'',''旗山區'',''彌陀區'',''納瑪夏區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300)
    )
    AND saledays <= 270
    AND (TRY_CAST(low AS FLOAT) >= 2)
    AND type IN (''大樓'',''住宅大樓'',''套房'',''華廈'',''電梯大廈'',''電梯大樓'',''電梯住宅'')
GROUP BY ym, city
ORDER BY city, ym';

-- 執行動態 SQL
EXEC sp_executesql @sql;