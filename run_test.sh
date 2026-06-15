#!/bin/bash
# 系统功能测试脚本 — 数据层 + API 层全覆盖
OUTPUT=/home/wonseok/tmp/test_results.txt
echo "============================================================" | tee $OUTPUT
echo "  市域生态环境智慧监测感知大数据中枢 — 系统功能测试" | tee -a $OUTPUT
echo "  测试时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a $OUTPUT
echo "============================================================" | tee -a $OUTPUT

# ==========================================
# 第一部分: 数据层测试
# ==========================================
echo "" | tee -a $OUTPUT
echo "########## 一、数据层测试 ##########" | tee -a $OUTPUT

# 测试1: 数据库存在性
echo "" | tee -a $OUTPUT
echo "--- 测试1: SHOW DATABASES ---" | tee -a $OUTPUT
hive --silent -e "SHOW DATABASES;" 2>/dev/null | tee -a $OUTPUT

# 测试2: 表列表
echo "" | tee -a $OUTPUT
echo "--- 测试2: SHOW TABLES IN environment ---" | tee -a $OUTPUT
hive --silent -e "USE environment; SHOW TABLES;" 2>/dev/null | tee -a $OUTPUT

# 测试3: 核心表行数
echo "" | tee -a $OUTPUT
echo "--- 测试3: 核心表 COUNT 统计 ---" | tee -a $OUTPUT
for tbl in station_realtime_agg kpi_daily_agg pollution_source_agg air_quality_timeseries water_quality_timeseries district_overview emission_rank factory_list control_compare_timeseries control_measures_status emission_reduction_agg active_incidents rescue_teams_status rescue_gantt_tasks impact_radius_prediction river_section_realtime coverage_grid_analysis coverage_optimization_compare; do
  cnt=$(hive --silent -e "USE environment; SELECT COUNT(*) FROM $tbl;" 2>/dev/null | tail -1)
  echo "  $tbl: $cnt" | tee -a $OUTPUT
done

# 测试4: 数据总量
echo "" | tee -a $OUTPUT
echo "--- 测试4: 数据总量汇总 ---" | tee -a $OUTPUT
total=0
for tbl in station_realtime_agg air_quality_timeseries water_quality_timeseries district_overview emission_rank factory_list control_compare_timeseries control_measures_status emission_reduction_agg active_incidents rescue_teams_status rescue_gantt_tasks impact_radius_prediction river_section_realtime coverage_grid_analysis coverage_optimization_compare; do
  cnt=$(hive --silent -e "USE environment; SELECT COUNT(*) FROM $tbl;" 2>/dev/null | tail -1)
  total=$((total + cnt))
done
echo "  总计: $total 条 (需求: >=50000)" | tee -a $OUTPUT
[ $total -ge 50000 ] && echo "  结果: ✅ 达标" | tee -a $OUTPUT || echo "  结果: ❌ 不达标" | tee -a $OUTPUT

# 测试5: 数据抽样验证
echo "" | tee -a $OUTPUT
echo "--- 测试5: station_realtime_agg 抽样 (前3行) ---" | tee -a $OUTPUT
hive --silent -e "USE environment; SELECT id, name, type, pm25, aqi, status FROM station_realtime_agg LIMIT 3;" 2>/dev/null | tee -a $OUTPUT

# ==========================================
# 第二部分: API 接口测试
# ==========================================
echo "" | tee -a $OUTPUT
echo "########## 二、API 接口测试 ##########" | tee -a $OUTPUT
API="http://127.0.0.1:8080/api"
pass=0; fail=0

test_api() {
  local path="$1" desc="$2"
  local code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 90 "${API}${path}" 2>/dev/null)
  if [ "$code" = "200" ]; then
    echo "  ✅ $desc — HTTP $code" | tee -a $OUTPUT
    pass=$((pass+1))
  else
    echo "  ❌ $desc — HTTP $code" | tee -a $OUTPUT
    fail=$((fail+1))
  fi
}

# Scene 1 (7个)
test_api "/stations/realtime"         "GET 监测站实时数据"
test_api "/kpi/overview"              "GET KPI全景指标"
test_api "/pollution/sources"         "GET 污染源类型占比"
test_api "/air/trend?hours=6"         "GET 空气趋势(6h)"
test_api "/water/trend?days=3"        "GET 水质趋势(3天)"
test_api "/districts/overview"        "GET 各区环境概况"
test_api "/emission/rank"             "GET 排放排行"

# Scene 2 (4个)
test_api "/pollution/factories"       "GET 重点工厂列表"
test_api "/pollution/control-compare" "GET 管控前后对比"
test_api "/pollution/control-measures" "GET 管控措施执行率"
test_api "/pollution/reduction-rate"  "GET 总体减排率"

# Scene 3 (5个)
test_api "/emergency/incident"        "GET 当前事故信息"
test_api "/emergency/rescue-teams"    "GET 救援队伍位置"
test_api "/emergency/gantt"           "GET 救援甘特图"
test_api "/emergency/impact-prediction" "GET 影响范围预测"
test_api "/emergency/topology"        "GET 应急拓扑网络"

# Scene 4 (2个)
test_api "/water/river-sections"      "GET 河流断面数据"
test_api "/water/sankey"              "GET 污染源→断面桑基图"

# Scene 5 (2个)
test_api "/coverage/grid"             "GET 监测覆盖网格"
test_api "/coverage/compare"          "GET 覆盖率优化对比"

echo "" | tee -a $OUTPUT
echo "  通过: $pass / 失败: $fail / 总计: 20" | tee -a $OUTPUT
[ $fail -eq 0 ] && echo "  结果: ✅ 全部通过" | tee -a $OUTPUT || echo "  结果: ❌ 存在失败" | tee -a $OUTPUT

# ==========================================
# 第三部分: JSON 结构验证
# ==========================================
echo "" | tee -a $OUTPUT
echo "########## 三、JSON 响应结构验证 ##########" | tee -a $OUTPUT

echo "" | tee -a $OUTPUT
echo "--- GET /api/kpi/overview 响应体 ---" | tee -a $OUTPUT
curl -s "${API}/kpi/overview" | python3 -m json.tool 2>/dev/null | tee -a $OUTPUT

echo "" | tee -a $OUTPUT
echo "--- GET /api/pollution/control-compare 响应体(truncated) ---" | tee -a $OUTPUT
curl -s "${API}/pollution/control-compare" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  predicted: {len(d[\"predicted\"])} 个元素, 前3个: {d[\"predicted\"][:3]}')
print(f'  controlled: {len(d[\"controlled\"])} 个元素, 前3个: {d[\"controlled\"][:3]}')
print(f'  labels: {len(d[\"labels\"])} 个元素, 前3个: {d[\"labels\"][:3]}')
" 2>/dev/null | tee -a $OUTPUT

echo "" | tee -a $OUTPUT
echo "--- GET /api/coverage/grid 响应体(truncated) ---" | tee -a $OUTPUT
curl -s "${API}/coverage/grid" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  总网格数: {len(d)}')
blind = [g for g in d if g.get('isBlindSpot')]
print(f'  盲区网格数: {len(blind)}')
print(f'  首网格: {json.dumps(d[0], ensure_ascii=False)}')
" 2>/dev/null | tee -a $OUTPUT

echo "" | tee -a $OUTPUT
echo "============================================================" | tee -a $OUTPUT
echo "  测试完成: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a $OUTPUT
echo "============================================================" | tee -a $OUTPUT
