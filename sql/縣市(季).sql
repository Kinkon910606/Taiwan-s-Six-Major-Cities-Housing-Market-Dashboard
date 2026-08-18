---- 主要改動說明：
-- D_GIS_全國 開頭：使用 LIKE 'D_GIS_全國%' 並取最新的一個（ORDER BY TABLE_NAME DESC）
-- A_W 開頭：動態產生所有 A_W 開頭的資料表並用 UNION ALL 串接
-- D_折價明細_全國 開頭：使用 LIKE 'D_折價明細_全國%' 並取最新的一個
-- 移轉棟數 結尾：使用 LIKE '%移轉棟數' 並取最新的一個

DECLARE @sql NVARCHAR(MAX) = '';
DECLARE @sqlGIS NVARCHAR(MAX) = '';
DECLARE @sqlAW NVARCHAR(MAX) = '';
DECLARE @sqlDiscount NVARCHAR(MAX) = '';
DECLARE @sqlTransfer NVARCHAR(MAX) = '';

-- 1. 動態產生 D_GIS_全國 開頭的資料表 (只取第一個，因為原本就只有一個)
SELECT TOP 1 @sqlGIS = QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE 'D_GIS_全國%'
ORDER BY TABLE_NAME DESC;

-- 2. 動態產生 A_W 開頭的資料表 UNION ALL
SELECT @sqlAW = @sqlAW + 
    'SELECT * FROM ' + QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) + ' UNION ALL '
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE 'A_W%'
ORDER BY TABLE_NAME;
SET @sqlAW = LEFT(@sqlAW, LEN(@sqlAW) - 10); -- 移除最後的 UNION ALL

-- 3. 動態產生 D_折價明細_全國 開頭的資料表 (只取第一個)
SELECT TOP 1 @sqlDiscount = QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE 'D_折價明細_全國%'
ORDER BY TABLE_NAME DESC;

-- 4. 動態產生 移轉棟數 結尾的資料表 (只取第一個)
SELECT TOP 1 @sqlTransfer = QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE '%移轉棟數'
ORDER BY TABLE_NAME DESC;

-- 組合完整的查詢
SET @sql = '
WITH cte0 AS (
SELECT 縣市 ,交易季, ROUND(AVG(合併單價), 2) AS 平均成交單價, COUNT(*) as [交易量(棟)]
FROM ' + @sqlGIS + '
WHERE 
    /*** 地區 ***/
    ((縣市 = ''臺北市'' AND 扣車坪 Between 5 and 400 AND 合併單價 between 5 and 400) OR
    (縣市 = ''新北市'' AND 鄉鎮市區 not in (''萬里區'',''金山區'',''貢寮區'',''雙溪區'',''瑞芳區'',''平溪區'',''石碇區'',''坪林區'',''烏來區'',''三芝區'',''石門區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) OR
    (縣市 = ''桃園市'' AND 鄉鎮市區 not in (''新屋區'',''觀音區'',''大溪區'',''復興區'',''龍潭區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) OR
    (縣市 = ''臺中市'' AND 鄉鎮市區 not in (''大甲區'',''大安區'',''外埔區'',''東勢區'',''和平區'',''清水區'',''石岡區'',''新社區'',''梧棲區'',''霧峰區'',''沙鹿區'',''大肚區'',''后里區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) OR
    (縣市 = ''臺南市'' AND 鄉鎮市區 not in (''七股區'',''下營區'',''六甲區'',''左鎮區'',''玉井區'',''白河區'',''西港區'',''安定區'',''官田區'',''東山區'',''南化區'',''後壁區'',''柳營區'',''麻豆區'',
                                    ''將軍區'',''楠西區'',''龍崎區'',''學甲區'',''關廟區'',''鹽水區'',''大內區'',''山上區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) OR
    (縣市 = ''高雄市'' AND 鄉鎮市區 not in (''鳥松區'',''旗津區'',''大寮區'',''大社區'',''林園區'',''路竹區'',''燕巢區'',''梓官區'',''大樹區'',''六龜區'',''內門區'',''田寮區'',''永安區'',''甲仙區'',''杉林區'',
                                    ''阿蓮區'',''美濃區'',''桃源區'',''梓官區'',''茂林區'',''茄定區'',''茄萣區'',''湖內區'',''旗山區'',''彌陀區'',''納瑪夏區'') AND 扣車坪 Between 5 and 300 AND 合併單價 between 5 and 300) 
    ) AND
    /*** 其他條件 ***/
    交易年月 >= 202401 AND 交易年月 <= 210000 AND
    最低樓層 >= 2 AND
    建物類別名稱 in (''住宅大樓(11層含以上有電梯)'',''華廈(10層含以下有電梯)'') AND
    特殊交易 != ''L''
GROUP BY 縣市 , 交易季
),
cte1 AS (
SELECT
    CONVERT(varchar, left(ym,4))+''Q''+ CONVERT(varchar, (right(ym,2)-1)/3+1) AS 交易季, 
    REPLACE(city, ''台'', ''臺'') AS 縣市, ROUND(AVG(unit), 2) AS 平均開價單價
FROM (' + @sqlAW + ') aw_union
WHERE 
    /*** 地區 ***/
    ((city = ''台北市'' AND size Between 5 and 400 AND unit between 5 and 400) OR
    (city = ''新北市'' AND dist not in (''萬里區'',''金山區'',''貢寮區'',''雙溪區'',''瑞芳區'',''平溪區'',''石碇區'',''坪林區'',''烏來區'',''三芝區'',''石門區'') AND size Between 5 and 300 AND unit between 5 and 300) OR
    (city = ''桃園市'' AND dist not in (''新屋區'',''觀音區'',''大溪區'',''復興區'',''龍潭區'') AND size Between 5 and 300 AND unit between 5 and 300) OR
    (city = ''台中市'' AND dist not in (''大甲區'',''大安區'',''外埔區'',''東勢區'',''和平區'',''清水區'',''石岡區'',''新社區'',''梧棲區'',''霧峰區'',''沙鹿區'',''大肚區'',''后里區'') AND size Between 5 and 300 AND unit between 5 and 300) OR
    (city = ''台南市'' AND dist not in (''七股區'',''下營區'',''六甲區'',''左鎮區'',''玉井區'',''白河區'',''西港區'',''安定區'',''官田區'',''東山區'',''南化區'',''後壁區'',''柳營區'',''麻豆區'',
                                    ''將軍區'',''楠西區'',''龍崎區'',''學甲區'',''關廟區'',''鹽水區'',''大內區'',''山上區'') AND size Between 5 and 300 AND unit between 5 and 300) OR
    (city = ''高雄市'' AND dist not in (''鳥松區'',''旗津區'',''大寮區'',''大社區'',''林園區'',''路竹區'',''燕巢區'',''梓官區'',''大樹區'',''六龜區'',''內門區'',''田寮區'',''永安區'',''甲仙區'',''杉林區'',
                                    ''阿蓮區'',''美濃區'',''桃源區'',''梓官區'',''茂林區'',''茄定區'',''茄萣區'',''湖內區'',''旗山區'',''彌陀區'',''納瑪夏區'') AND size Between 5 and 300 AND unit between 5 and 300) 
    )
    /*** 其餘條件 ***/
    AND ym >= 202401
    AND saledays<=270
    AND  (try_CAST(low AS FLOAT)>=2 )
    AND type in (''大樓'',''住宅大樓'',''套房'',''華廈'',''電梯大廈'',''電梯大樓'',''電梯住宅'')
GROUP BY city, CONVERT(varchar, left(ym,4))+''Q''+ CONVERT(varchar, (right(ym,2)-1)/3+1)
),
cte2 AS (
SELECT REPLACE(縣市,''台'',''臺'') AS 縣市 , 成交季 AS 交易季,
ROUND(AVG(銷售天期), 1) AS 平均銷售天期, ROUND(AVG(折價率), 3) AS 平均折價率
FROM ' + @sqlDiscount + '
WHERE 成交年月 >= 202401  AND
    ((縣市 = ''臺北市'' AND 成交建坪 Between 5 and 400 AND 成交單價 between 5 and 400) OR
    (縣市 = ''新北市'' AND 鄉鎮市區 not in (''萬里區'',''金山區'',''貢寮區'',''雙溪區'',''瑞芳區'',''平溪區'',''石碇區'',''坪林區'',''烏來區'',''三芝區'',''石門區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) OR
    (縣市 = ''桃園市'' AND 鄉鎮市區 not in (''新屋區'',''觀音區'',''大溪區'',''復興區'',''龍潭區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) OR
    (縣市 = ''臺中市'' AND 鄉鎮市區 not in (''大甲區'',''大安區'',''外埔區'',''東勢區'',''和平區'',''清水區'',''石岡區'',''新社區'',''梧棲區'',''霧峰區'',''沙鹿區'',''大肚區'',''后里區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) OR
    (縣市 = ''臺南市'' AND 鄉鎮市區 not in (''七股區'',''下營區'',''六甲區'',''左鎮區'',''玉井區'',''白河區'',''西港區'',''安定區'',''官田區'',''東山區'',''南化區'',''後壁區'',''柳營區'',''麻豆區'',
                                    ''將軍區'',''楠西區'',''龍崎區'',''學甲區'',''關廟區'',''鹽水區'',''大內區'',''山上區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) OR
    (縣市 = ''高雄市'' AND 鄉鎮市區 not in (''鳥松區'',''旗津區'',''大寮區'',''大社區'',''林園區'',''路竹區'',''燕巢區'',''梓官區'',''大樹區'',''六龜區'',''內門區'',''田寮區'',''永安區'',''甲仙區'',''杉林區'',
                                    ''阿蓮區'',''美濃區'',''桃源區'',''梓官區'',''茂林區'',''茄定區'',''茄萣區'',''湖內區'',''旗山區'',''彌陀區'',''納瑪夏區'') AND 成交建坪 Between 5 and 300 AND 成交單價 between 5 and 300) 
    )
GROUP BY 縣市, 成交季
),
cte3 AS (
SELECT 縣市, 交易季,sum([移轉登記買賣棟數]) AS [交易量(棟)]
FROM (SELECT *, CONVERT(varchar, 年)+''Q''+  CONVERT(varchar, round((月-1)/3+1, 0, 1)) AS 交易季 FROM ' + @sqlTransfer + ') a
WHERE 縣市 in (''臺北市'',''新北市'',''桃園市'',''臺中市'',''臺南市'',''高雄市'') AND
    年*100+月 >= 202401 
GROUP BY 縣市, 交易季
)
SELECT a.縣市, a.交易季, d.[交易量(棟)] , a.平均成交單價 AS [成交行情(萬/坪)], b.平均開價單價 AS [市場開價(萬/坪)],
    c.平均銷售天期 AS [銷售天期(天)],  round(c.平均折價率*100,2) AS [買賣議價率(%)]
FROM 
cte0 a 
FULL JOIN cte1 b on a.縣市 = b.縣市 AND a.交易季 = b.交易季 
FULL JOIN cte2 c on a.縣市 = c.縣市 AND a.交易季 = c.交易季 
FULL JOIN cte3 d on a.縣市 = d.縣市 AND a.交易季 = d.交易季 
WHERE a.縣市 IS NOT NULL
';

-- 執行動態 SQL
EXEC sp_executesql @sql;