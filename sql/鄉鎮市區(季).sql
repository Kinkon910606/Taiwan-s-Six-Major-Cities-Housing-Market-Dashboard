DECLARE @sql NVARCHAR(MAX) = '';
DECLARE @sqlGIS NVARCHAR(MAX) = '';
DECLARE @sqlAW NVARCHAR(MAX) = '';
DECLARE @sqlDiscount NVARCHAR(MAX) = '';

-- 1. 動態產生 D_GIS_全國 開頭的資料表 (取最新的一個)
SELECT TOP 1 @sqlGIS = QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE 'D_GIS_全國%'
ORDER BY TABLE_NAME DESC;

-- 2. 動態產生所有 A_W 開頭的資料表 UNION ALL
SELECT @sqlAW = @sqlAW + 
    'SELECT city, dist, type, unit, size, saledays, low, ym FROM ' + 
    QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) + 
    ' WHERE saledays <= 270 UNION ALL '
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE 'A_W%'
ORDER BY TABLE_NAME;
SET @sqlAW = LEFT(@sqlAW, LEN(@sqlAW) - 10); -- 移除最後的 UNION ALL

-- 3. 動態產生 D_折價明細_全國 開頭的資料表 (取最新的一個)
SELECT TOP 1 @sqlDiscount = QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE 'D_折價明細_全國%'
ORDER BY TABLE_NAME DESC;

-- 組合完整的查詢
SET @sql = '
WITH cte0 AS (
    SELECT 
        縣市, 鄉鎮市區, 交易季, 建物大類 AS 建物類別名稱, ROUND(AVG(合併單價), 2) AS 平均成交單價, COUNT(*) AS [交易量(棟)]
    FROM (
        SELECT *,
            CASE 
                WHEN 建物類別名稱=''套房(1房1廳1衛)'' THEN N''住宅大樓''
                WHEN 建物類別名稱=''住宅大樓(11層含以上有電梯)'' THEN N''住宅大樓''
                WHEN 建物類別名稱=''公寓(5樓含以下無電梯)'' THEN N''公寓''
                WHEN 建物類別名稱=''華廈(10層含以下有電梯)'' THEN N''住宅大樓''
                WHEN 建物類別名稱=''透天厝'' THEN N''透天厝''
                ELSE ''ERROR'' 
            END AS 建物大類
        FROM ' + @sqlGIS + '
        WHERE 
            /*** 地區 ***/
            ((縣市 = ''臺北市'' AND 扣車坪 Between 5 and 400 AND 合併單價 between 5 and 400) OR
            (縣市 = ''新北市'' AND 鄉鎮市區 not in (''萬里區'',''金山區'',''貢寮區'',''雙溪區'',''瑞芳區'',''平溪區'',''石碇區'',''坪林區'',''烏來區'',''三芝區'',''石門區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) OR
            (縣市 = ''桃園市'' AND 鄉鎮市區 not in (''新屋區'',''觀音區'',''大溪區'',''復興區'',''龍潭區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) OR
            (縣市 = ''臺中市'' AND 鄉鎮市區 not in (''大甲區'',''大安區'',''外埔區'',''東勢區'',''和平區'',''清水區'',''石岡區'',''新社區'',''梧棲區'',''霧峰區'',''沙鹿區'',''大肚區'',''后里區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) OR
            (縣市 = ''臺南市'' AND 鄉鎮市區 not in (''北門區'',''七股區'',''下營區'',''六甲區'',''左鎮區'',''玉井區'',''白河區'',''西港區'',''安定區'',''官田區'',''東山區'',''南化區'',''後壁區'',''柳營區'',''麻豆區'',
                                                ''將軍區'',''楠西區'',''龍崎區'',''學甲區'',''關廟區'',''鹽水區'',''大內區'',''山上區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) OR
            (縣市 = ''高雄市'' AND 鄉鎮市區 not in (''那瑪夏區'',''鳥松區'',''旗津區'',''大寮區'',''大社區'',''林園區'',''路竹區'',''燕巢區'',''梓官區'',''大樹區'',''六龜區'',''內門區'',''田寮區'',''永安區'',''甲仙區'',''杉林區'',
                                                ''阿蓮區'',''美濃區'',''桃源區'',''梓官區'',''茂林區'',''茄定區'',''茄萣區'',''湖內區'',''旗山區'',''彌陀區'',''納瑪夏區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) 
            ) AND
            /*** 其他條件 ***/
            交易年月 >= 202401 AND 交易年月 < 210000 AND
            ((建物類別名稱=''透天厝'' AND 最低樓層 >= 1) OR (建物類別名稱 in (''公寓(5樓含以下無電梯)'',''住宅大樓(11層含以上有電梯)'',''華廈(10層含以下有電梯)'',''套房(1房1廳1衛)'') AND 最低樓層 >= 2))AND
            特殊交易 != ''L''
    ) AS A
    GROUP BY  縣市, 鄉鎮市區, 交易季, 建物大類
),
cte1 AS (
    SELECT 
        縣市, 
        鄉鎮市區, 
        建物類別名稱, 
        交易季,
        ROUND(AVG(unit), 2) AS 平均開價單價, 
        COUNT(*) AS NUM
    FROM (
        SELECT 
            REPLACE(a.city, ''台'', ''臺'') AS 縣市,
            a.dist AS 鄉鎮市區,
            CONVERT(varchar, left(a.ym,4))+''Q''+ CONVERT(varchar, (right(a.ym,2)-1)/3+1) AS 交易季, 
            CASE 
                WHEN a.type IN (''電梯大樓'',''大樓'',''住宅大樓'',''電梯住宅'',''套房'',''華廈'',''電梯大廈'')  THEN N''住宅大樓''
                WHEN a.type IN (''公寓'') THEN N''公寓''
                WHEN a.type IN (''透天厝'',''別墅'',''透天'',''透天別墅'',''別墅/透天'',''店面別墅/透天'') THEN N''透天厝''
                ELSE ''error''
            END AS 建物類別名稱,
            a.unit
        FROM (' + @sqlAW + ') a
        WHERE 
            -- 地區條件
            (
                (a.city = ''台北市'' AND a.size BETWEEN 5 AND 400 AND a.unit BETWEEN 5 AND 400) OR
                (a.city = ''新北市'' AND a.dist NOT IN (''萬里區'',''金山區'',''貢寮區'',''雙溪區'',''瑞芳區'',''平溪區'',''石碇區'',''坪林區'',''烏來區'',''三芝區'',''石門區'') 
                    AND a.size BETWEEN 5 AND 300 AND a.unit BETWEEN 5 AND 300) OR
                (a.city = ''桃園市'' AND a.dist NOT IN (''新屋區'',''觀音區'',''大溪區'',''復興區'',''龍潭區'') 
                    AND a.size BETWEEN 5 AND 300 AND a.unit BETWEEN 5 AND 300) OR
                (a.city = ''台中市'' AND a.dist NOT IN (''大甲區'',''大安區'',''外埔區'',''東勢區'',''和平區'',''清水區'',''石岡區'',''新社區'',''梧棲區'',''霧峰區'',''沙鹿區'',''大肚區'',''后里區'') 
                    AND a.size BETWEEN 5 AND 300 AND a.unit BETWEEN 5 AND 300) OR
                (a.city = ''台南市'' AND a.dist NOT IN (''北門區'',''七股區'',''下營區'',''六甲區'',''左鎮區'',''玉井區'',''白河區'',''西港區'',''安定區'',''官田區'',''東山區'',''南化區'',''後壁區'',''柳營區'',''麻豆區'',
                                                    ''將軍區'',''楠西區'',''龍崎區'',''學甲區'',''關廟區'',''鹽水區'',''大內區'',''山上區'') 
                    AND a.size BETWEEN 5 AND 300 AND a.unit BETWEEN 5 AND 300) OR
                (a.city = ''高雄市'' AND a.dist NOT IN (''那瑪夏區'',''鳥松區'',''旗津區'',''大寮區'',''大社區'',''林園區'',''路竹區'',''燕巢區'',''梓官區'',''大樹區'',''六龜區'',''內門區'',''田寮區'',''永安區'',''甲仙區'',''杉林區'',
                                                    ''阿蓮區'',''美濃區'',''桃源區'',''梓官區'',''茂林區'',''茄定區'',''茄萣區'',''湖內區'',''旗山區'',''彌陀區'',''納瑪夏區'') 
                    AND a.size BETWEEN 5 AND 300 AND a.unit BETWEEN 5 AND 300)
            )
            -- 樓層條件
            AND (
                (TRY_CAST(a.low AS FLOAT) >= 2 AND a.type IN (''電梯大樓'',''公寓'',''大樓'',''華廈'',''電梯大廈'',''住宅大樓'',''套房'',''電梯住宅'')) 
                OR (TRY_CAST(a.low AS FLOAT) >= 1 AND a.type IN (''透天厝'',''別墅'',''透天'',''透天別墅'',''別墅/透天'',''店面別墅/透天''))
            )
            AND ym >= 202401
    ) AS filtered_data
    GROUP BY 縣市, 鄉鎮市區, 建物類別名稱, 交易季
),
cte2 AS (
    SELECT 縣市,  鄉鎮市區, 交易季, 建物a AS 建物類別名稱, 
    ROUND(AVG(銷售天期), 1) AS 平均銷售天期, ROUND(AVG(折價率), 3) AS 平均折價率
    FROM (
        SELECT 
            REPLACE(縣市,''台'',''臺'') AS 縣市 ,鄉鎮市區, 
            CASE WHEN 建物類別名稱=''套房(1房1廳1衛)'' THEN N''住宅大樓'' 
                    WHEN 建物類別名稱=''住宅大樓(11層含以上有電梯)'' THEN N''住宅大樓''
                    WHEN 建物類別名稱=''公寓(5樓含以下無電梯)'' THEN N''公寓''
                    WHEN 建物類別名稱=''華廈(10層含以下有電梯)'' THEN N''住宅大樓''
                    WHEN 建物類別名稱=''透天厝'' THEN N''透天厝''
                    ELSE ''ERROR'' END AS 建物a,
            CONVERT(varchar, left(成交年月,4))+''Q''+ CONVERT(varchar, (right(成交年月,2)-1)/3+1) AS 交易季,
            銷售天期, 折價率
            
        FROM ' + @sqlDiscount + '
        WHERE 成交年月 >= 202401 and 成交年月 < 210000 
            AND ((縣市 = ''臺北市'' AND 成交建坪 Between 5 and 400 AND 成交單價 between 5 and 400) OR
            (縣市 = ''新北市'' AND 鄉鎮市區 not in (''萬里區'',''金山區'',''貢寮區'',''雙溪區'',''瑞芳區'',''平溪區'',''石碇區'',''坪林區'',''烏來區'',''三芝區'',''石門區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) OR
            (縣市 = ''桃園市'' AND 鄉鎮市區 not in (''新屋區'',''觀音區'',''大溪區'',''復興區'',''龍潭區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) OR
            (縣市 = ''臺中市'' AND 鄉鎮市區 not in (''大甲區'',''大安區'',''外埔區'',''東勢區'',''和平區'',''清水區'',''石岡區'',''新社區'',''梧棲區'',''霧峰區'',''沙鹿區'',''大肚區'',''后里區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) OR
            (縣市 = ''臺南市'' AND 鄉鎮市區 not in (''北門區'',''七股區'',''下營區'',''六甲區'',''左鎮區'',''玉井區'',''白河區'',''西港區'',''安定區'',''官田區'',''東山區'',''南化區'',''後壁區'',''柳營區'',''麻豆區'',
                                                ''將軍區'',''楠西區'',''龍崎區'',''學甲區'',''關廟區'',''鹽水區'',''大內區'',''山上區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) OR
            (縣市 = ''高雄市'' AND 鄉鎮市區 not in (''那瑪夏區'',''鳥松區'',''旗津區'',''大寮區'',''大社區'',''林園區'',''路竹區'',''燕巢區'',''梓官區'',''大樹區'',''六龜區'',''內門區'',''田寮區'',''永安區'',''甲仙區'',''杉林區'',
                                                ''阿蓮區'',''美濃區'',''桃源區'',''梓官區'',''茂林區'',''茄定區'',''茄萣區'',''湖內區'',''旗山區'',''彌陀區'',''納瑪夏區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) 
            )
            AND (([建物類別名稱]=''透天厝'' AND [成交移轉層次] >= 1) 
                OR 
                ([建物類別名稱] in (''公寓(5樓含以下無電梯)'',''住宅大樓(11層含以上有電梯)'',''華廈(10層含以下有電梯)'',''套房(1房1廳1衛)'') AND [成交移轉層次] >= 2))
    ) AS A
    GROUP BY 縣市, 鄉鎮市區,建物a, 交易季
)
SELECT a.縣市, a.鄉鎮市區 AS 行政區,a.建物類別名稱, a.交易季, a.[交易量(棟)], a.平均成交單價 AS [成交行情(萬/坪)], b.平均開價單價 AS [市場開價(萬/坪)],
       c.平均銷售天期 AS [銷售天期(天)],  CONVERT(varchar, c.平均折價率*100)+''%'' AS [買賣議價率(%)]
FROM 
    cte0 a 
    FULL JOIN cte1 b on a.縣市 = b.縣市 AND a.交易季 = b.交易季 AND a.鄉鎮市區 = b.鄉鎮市區 AND a.建物類別名稱 = b.建物類別名稱
    FULL JOIN cte2 c on a.縣市 = c.縣市 AND a.交易季 = c.交易季 AND a.鄉鎮市區 = c.鄉鎮市區 AND a.建物類別名稱 = c.建物類別名稱
WHERE a.交易季 is not NULL
';

-- 執行動態 SQL
EXEC sp_executesql @sql;