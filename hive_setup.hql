-- ============================================================
-- 市域生态环境智慧监测感知大数据中枢 Hive 建表与数据加载
-- ============================================================

CREATE DATABASE IF NOT EXISTS environment;
USE environment;

-- ============================================================
-- 1. 监测站实时数据 (50行)
-- ============================================================
DROP TABLE IF EXISTS station_realtime_agg;
CREATE TABLE station_realtime_agg (
    id INT,
    name STRING,
    type INT,
    lng DOUBLE,
    lat DOUBLE,
    pm25 STRING,
    pm10 STRING,
    so2 STRING,
    no2 STRING,
    aqi INT,
    waterQuality STRING,
    cod STRING,
    nh3n STRING,
    status STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/station_realtime_agg.csv'
INTO TABLE station_realtime_agg;

-- ============================================================
-- 2. KPI 指标 (1行)
-- ============================================================
DROP TABLE IF EXISTS kpi_daily_agg;
CREATE TABLE kpi_daily_agg (
    airRate DOUBLE,
    waterRate DOUBLE,
    alarmCount INT,
    airTrend DOUBLE,
    waterTrend DOUBLE,
    alarmTrend INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/kpi_daily_agg.csv'
INTO TABLE kpi_daily_agg;

-- ============================================================
-- 3. 污染源类型占比 (5行)
-- ============================================================
DROP TABLE IF EXISTS pollution_source_agg;
CREATE TABLE pollution_source_agg (
    name STRING,
    value DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/pollution_source_agg.csv'
INTO TABLE pollution_source_agg;

-- ============================================================
-- 4. 空气质量时间序列 (~64,800行)
-- ============================================================
DROP TABLE IF EXISTS air_quality_timeseries;
CREATE TABLE air_quality_timeseries (
    station_id INT,
    time_val STRING,
    value_val STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/air_quality_timeseries.csv'
INTO TABLE air_quality_timeseries;

-- ============================================================
-- 5. 水质时间序列 (~21,600行)
-- ============================================================
DROP TABLE IF EXISTS water_quality_timeseries;
CREATE TABLE water_quality_timeseries (
    station_id INT,
    time_val STRING,
    value_val STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/water_quality_timeseries.csv'
INTO TABLE water_quality_timeseries;

-- ============================================================
-- 6. 各区概况 (6行)
-- ============================================================
DROP TABLE IF EXISTS district_overview;
CREATE TABLE district_overview (
    name STRING,
    aqi INT,
    pm25 DOUBLE,
    waterRate DOUBLE,
    alarmCount INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/district_overview.csv'
INTO TABLE district_overview;

-- ============================================================
-- 7. 排放排行 (10行)
-- ============================================================
DROP TABLE IF EXISTS emission_rank;
CREATE TABLE emission_rank (
    id INT,
    name STRING,
    aqi INT,
    pm25 DOUBLE,
    so2 DOUBLE,
    no2 DOUBLE,
    status STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/emission_rank.csv'
INTO TABLE emission_rank;

-- ============================================================
-- 8. 工厂列表 (4行)
-- ============================================================
DROP TABLE IF EXISTS factory_list;
CREATE TABLE factory_list (
    name STRING,
    lng DOUBLE,
    lat DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/factory_list.csv'
INTO TABLE factory_list;

-- ============================================================
-- 9. 管控对比时间序列 (48行)
-- ============================================================
DROP TABLE IF EXISTS control_compare_timeseries;
CREATE TABLE control_compare_timeseries (
    hour INT,
    label STRING,
    predicted STRING,
    controlled STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/control_compare_timeseries.csv'
INTO TABLE control_compare_timeseries;

-- ============================================================
-- 10. 管控措施执行率 (5行)
-- ============================================================
DROP TABLE IF EXISTS control_measures_status;
CREATE TABLE control_measures_status (
    name STRING,
    rate INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/control_measures_status.csv'
INTO TABLE control_measures_status;

-- ============================================================
-- 11. 减排率 (1行)
-- ============================================================
DROP TABLE IF EXISTS emission_reduction_agg;
CREATE TABLE emission_reduction_agg (
    value DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/emission_reduction_agg.csv'
INTO TABLE emission_reduction_agg;

-- ============================================================
-- 12. 事故信息 (1行)
-- ============================================================
DROP TABLE IF EXISTS active_incidents;
CREATE TABLE active_incidents (
    name STRING,
    lng DOUBLE,
    lat DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/active_incidents.csv'
INTO TABLE active_incidents;

-- ============================================================
-- 13. 救援队伍 (6行)
-- ============================================================
DROP TABLE IF EXISTS rescue_teams_status;
CREATE TABLE rescue_teams_status (
    name STRING,
    lng DOUBLE,
    lat DOUBLE,
    eta INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/rescue_teams_status.csv'
INTO TABLE rescue_teams_status;

-- ============================================================
-- 14. 救援甘特图 (7行)
-- ============================================================
DROP TABLE IF EXISTS rescue_gantt_tasks;
CREATE TABLE rescue_gantt_tasks (
    task STRING,
    start_val INT,
    duration INT,
    dept STRING,
    status STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/rescue_gantt_tasks.csv'
INTO TABLE rescue_gantt_tasks;

-- ============================================================
-- 15. 影响范围预测 (7行)
-- ============================================================
DROP TABLE IF EXISTS impact_radius_prediction;
CREATE TABLE impact_radius_prediction (
    time_val STRING,
    area DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/impact_radius_prediction.csv'
INTO TABLE impact_radius_prediction;

-- ============================================================
-- 16A. 应急拓扑节点 (7行)
-- ============================================================
DROP TABLE IF EXISTS emergency_topology_nodes;
CREATE TABLE emergency_topology_nodes (
    name STRING,
    symbolSize INT,
    color STRING,
    x INT,
    y INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/emergency_topology_nodes.csv'
INTO TABLE emergency_topology_nodes;

-- ============================================================
-- 16B. 应急拓扑连线 (7行)
-- ============================================================
DROP TABLE IF EXISTS emergency_topology_links;
CREATE TABLE emergency_topology_links (
    source STRING,
    target STRING,
    color STRING,
    type STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/emergency_topology_links.csv'
INTO TABLE emergency_topology_links;

-- ============================================================
-- 17. 河流断面 (5行)
-- ============================================================
DROP TABLE IF EXISTS river_section_realtime;
CREATE TABLE river_section_realtime (
    name STRING,
    lng DOUBLE,
    lat DOUBLE,
    quality STRING,
    cod DOUBLE,
    nh3n DOUBLE,
    tp DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/river_section_realtime.csv'
INTO TABLE river_section_realtime;

-- ============================================================
-- 18A. 桑基图节点 (10行)
-- ============================================================
DROP TABLE IF EXISTS sankey_nodes;
CREATE TABLE sankey_nodes (
    name STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/sankey_nodes.csv'
INTO TABLE sankey_nodes;

-- ============================================================
-- 18B. 桑基图连线 (13行)
-- ============================================================
DROP TABLE IF EXISTS sankey_links;
CREATE TABLE sankey_links (
    source STRING,
    target STRING,
    value INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/sankey_links.csv'
INTO TABLE sankey_links;

-- ============================================================
-- 19. 覆盖网格 (36行)
-- ============================================================
DROP TABLE IF EXISTS coverage_grid_analysis;
CREATE TABLE coverage_grid_analysis (
    name STRING,
    lng DOUBLE,
    lat DOUBLE,
    stationCount INT,
    popDensity INT,
    isBlindSpot STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/coverage_grid_analysis.csv'
INTO TABLE coverage_grid_analysis;

-- ============================================================
-- 20. 覆盖率对比 (6行)
-- ============================================================
DROP TABLE IF EXISTS coverage_optimization_compare;
CREATE TABLE coverage_optimization_compare (
    category STRING,
    current_val INT,
    optimized INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

LOAD DATA LOCAL INPATH '/home/wonseok/tmp/csv_data/coverage_optimization_compare.csv'
INTO TABLE coverage_optimization_compare;

-- ============================================================
-- 验证
-- ============================================================
SELECT '=== station_realtime_agg ===' AS info;
SELECT COUNT(*) FROM station_realtime_agg;
SELECT '=== air_quality_timeseries ===' AS info;
SELECT COUNT(*) FROM air_quality_timeseries;
SELECT '=== water_quality_timeseries ===' AS info;
SELECT COUNT(*) FROM water_quality_timeseries;
