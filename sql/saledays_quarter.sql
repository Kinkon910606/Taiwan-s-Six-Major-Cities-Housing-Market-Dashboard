DECLARE @SQL NVARCHAR(MAX)
DECLARE @UnionSQL NVARCHAR(MAX) = ''

-- 自動計算當前的前一季和前前一季
DECLARE @CurrentYear INT = YEAR(GETDATE())
DECLARE @CurrentMonth INT = MONTH(GETDATE())
DECLARE @CurrentQuarter INT = CEILING(@CurrentMonth / 3.0)  -- 計算當前季度 (1-4)

DECLARE @Season0Year INT  -- 前前季的年份
DECLARE @Season0Quarter INT  -- 前前季的季度
DECLARE @Season1Year INT  -- 前一季的年份
DECLARE @Season1Quarter INT  -- 前一季的季度

-- 計算前一季 (Season1)
IF @CurrentQuarter = 1
BEGIN
    SET @Season1Year = @CurrentYear - 1
    SET @Season1Quarter = 4
END
ELSE
BEGIN
    SET @Season1Year = @CurrentYear
    SET @Season1Quarter = @CurrentQuarter - 1
END

-- 計算前前季 (Season0)
IF @Season1Quarter = 1
BEGIN
    SET @Season0Year = @Season1Year - 1
    SET @Season0Quarter = 4
END
ELSE
BEGIN
    SET @Season0Year = @Season1Year
    SET @Season0Quarter = @Season1Quarter - 1
END

-- 組合成季度字串
DECLARE @Season0 NVARCHAR(10) = CAST(@Season0Year AS NVARCHAR) + 'Q' + CAST(@Season0Quarter AS NVARCHAR)
DECLARE @Season1 NVARCHAR(10) = CAST(@Season1Year AS NVARCHAR) + 'Q' + CAST(@Season1Quarter AS NVARCHAR)

-- 動態產生所有 A_W 開頭的資料表 UNION ALL
SELECT @UnionSQL = @UnionSQL + 
    'SELECT * FROM ' + QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) + ' UNION ALL '
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE 'A_W%'
ORDER BY TABLE_NAME;

-- 移除最後一個 UNION ALL
SET @UnionSQL = LEFT(@UnionSQL, LEN(@UnionSQL) - 10);

-- 建立動態SQL
SET @SQL = N'
WITH cte AS (
    SELECT 
        CASE 
            WHEN RIGHT(ym, 2) <= ''03'' THEN LEFT(ym, 4) + ''Q1''
            WHEN RIGHT(ym, 2) <= ''06'' THEN LEFT(ym, 4) + ''Q2''
            WHEN RIGHT(ym, 2) <= ''09'' THEN LEFT(ym, 4) + ''Q3''
            WHEN RIGHT(ym, 2) <= ''12'' THEN LEFT(ym, 4) + ''Q4''
            ELSE ''impossible''
        END AS 交易季,
        *
    FROM (' + @UnionSQL + N') AS all_tables
    WHERE 
        (
            (city = ''台北市'' AND size BETWEEN 5 AND 400 AND unit BETWEEN 5 AND 400) OR
            (city = ''新北市'' AND dist NOT IN (''萬里區'',''金山區'',''貢寮區'',''雙溪區'',''瑞芳區'',''平溪區'',''石碇區'',''坪林區'',''烏來區'',''三芝區'',''石門區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300) OR
            (city = ''桃園市'' AND dist NOT IN (''新屋區'',''觀音區'',''大溪區'',''復興區'',''龍潭區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300) OR
            (city = ''台中市'' AND dist NOT IN (''大甲區'',''大安區'',''外埔區'',''東勢區'',''和平區'',''清水區'',''石岡區'',''新社區'',''梧棲區'',''霧峰區'',''沙鹿區'',''大肚區'',''后里區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300) OR
            (city = ''台南市'' AND dist NOT IN (''七股區'',''下營區'',''六甲區'',''左鎮區'',''玉井區'',''白河區'',''西港區'',''安定區'',''官田區'',''東山區'',''南化區'',''後壁區'',''柳營區'',''麻豆區'',
                                            ''將軍區'',''楠西區'',''龍崎區'',''學甲區'',''關廟區'',''鹽水區'',''大內區'',''山上區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300) OR
            (city = ''高雄市'' AND dist NOT IN (''鳥松區'',''旗津區'',''大寮區'',''大社區'',''林園區'',''路竹區'',''燕巢區'',''梓官區'',''大樹區'',''六龜區'',''內門區'',''田寮區'',''永安區'',''甲仙區'',''杉林區'',
                                            ''阿蓮區'',''美濃區'',''桃源區'',''梓官區'',''茂林區'',''茄定區'',''茄萣區'',''湖內區'',''旗山區'',''彌陀區'',''納瑪夏區'') AND size BETWEEN 5 AND 300 AND unit BETWEEN 5 AND 300)
        )
        AND saledays <= 270
        AND TRY_CAST(low AS FLOAT) >= 2
        AND type IN (''大樓'',''住宅大樓'',''套房'',''華廈'',''電梯大廈'',''電梯大樓'',''電梯住宅'')
)
SELECT
    REPLACE(city, ''台'', ''臺'') AS 縣市,
    dist AS 鄉鎮市區,
    ROUND(AVG(CASE WHEN 交易季 = @Season0 THEN saledays END), 0) AS [前季銷售天期],
    ROUND(AVG(CASE WHEN 交易季 = @Season1 THEN saledays END), 0) AS [當季銷售天期],
    ROUND( ( AVG(CASE WHEN 交易季 = @Season1 THEN saledays END) - AVG(CASE WHEN 交易季 = @Season0 THEN saledays END) )/
            NULLIF(AVG(CASE WHEN 交易季 = @Season0 THEN saledays END), 0) * 100 ,2) AS [增加率(%)] 
FROM cte
WHERE 交易季 IN (@Season0, @Season1)
GROUP BY city, dist
ORDER BY city, dist'

EXEC sp_executesql @SQL, N'@Season0 NVARCHAR(10), @Season1 NVARCHAR(10)', @Season0, @Season1

