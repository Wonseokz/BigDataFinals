#!/usr/bin/env python3
"""
市域生态环境智慧监测感知大数据中枢 — Flask REST API 后端
20个API端点, 查询 Hive 数据库并返回 JSON
"""
import subprocess
import json
import re
import os
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HIVE_DB = "environment"
hive_lock = threading.Lock()  # 防止并发 Hive CLI 调用冲突

def hive_query(sql, db=HIVE_DB):
    """执行 Hive 查询并返回行列表 (tab-separated)"""
    full_sql = f"USE {db}; {sql}"
    with hive_lock:
        try:
            result = subprocess.run(
                ['hive', '--silent', '-e', full_sql],
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ, 'HADOOP_USER_NAME': os.environ.get('USER', 'wonseok')}
            )
            if result.returncode != 0:
                print(f"[Hive Error] {result.stderr}")
                return []

            lines = result.stdout.strip().split('\n')
            rows = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('WARN:') or line == 'OK' or 'Time taken:' in line:
                    continue
                rows.append(line.split('\t'))
            return rows
        except subprocess.TimeoutExpired:
            print(f"[Timeout] Query took too long: {sql[:100]}")
            return []
        except Exception as e:
            print(f"[Error] {e}")
            return []


# ================================================================
# Scene 1: 全域环境态势一张图
# ================================================================

@app.route('/api/stations/realtime')
def stations_realtime():
    rows = hive_query("""
        SELECT id, name, type, lng, lat, pm25, pm10, so2, no2, aqi,
               waterQuality, cod, nh3n, status
        FROM station_realtime_agg
    """)
    result = []
    for r in rows:
        result.append({
            "id": int(r[0]),
            "name": r[1],
            "type": int(r[2]),
            "lng": float(r[3]),
            "lat": float(r[4]),
            "pm25": r[5],
            "pm10": r[6],
            "so2": r[7],
            "no2": r[8],
            "aqi": int(r[9]),
            "waterQuality": r[10],
            "cod": r[11],
            "nh3n": r[12],
            "status": r[13]
        })
    return jsonify(result)


@app.route('/api/kpi/overview')
def kpi_overview():
    rows = hive_query("SELECT * FROM kpi_daily_agg")
    if rows:
        r = rows[0]
        return jsonify({
            "airRate": float(r[0]),
            "waterRate": float(r[1]),
            "alarmCount": int(r[2]),
            "airTrend": float(r[3]),
            "waterTrend": float(r[4]),
            "alarmTrend": int(r[5])
        })
    return jsonify({})


@app.route('/api/pollution/sources')
def pollution_sources():
    rows = hive_query("SELECT * FROM pollution_source_agg")
    return jsonify([{"name": r[0], "value": float(r[1])} for r in rows])


@app.route('/api/air/trend')
def air_trend():
    hours = request.args.get('hours', 24, type=int)
    cutoff = (datetime.now() - timedelta(hours=hours + 1)).strftime('%Y-%m-%d %H:%M:%S')
    rows = hive_query(f"""
        SELECT time_val, value_val
        FROM air_quality_timeseries
        WHERE time_val >= '{cutoff}'
    """)
    result = []
    seen_times = set()
    for r in rows:
        time_str = r[0]
        try:
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            iso = dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        except:
            iso = time_str
        if iso not in seen_times:
            seen_times.add(iso)
            result.append({"time": iso, "value": r[1]})
        if len(result) >= hours:
            break
    result.sort(key=lambda x: x['time'])
    return jsonify(result)


@app.route('/api/water/trend')
def water_trend():
    days = request.args.get('days', 7, type=int)
    hours = days * 24
    cutoff = (datetime.now() - timedelta(days=days + 1)).strftime('%Y-%m-%d %H:%M:%S')
    rows = hive_query(f"""
        SELECT time_val, value_val
        FROM water_quality_timeseries
        WHERE time_val >= '{cutoff}'
    """)
    result = []
    seen_times = set()
    for r in rows:
        time_str = r[0]
        try:
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            iso = dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        except:
            iso = time_str
        if iso not in seen_times:
            seen_times.add(iso)
            result.append({"time": iso, "value": r[1]})
        if len(result) >= hours:
            break
    result.sort(key=lambda x: x['time'])
    return jsonify(result)


@app.route('/api/districts/overview')
def district_overview():
    rows = hive_query("SELECT * FROM district_overview")
    return jsonify([{
        "name": r[0],
        "aqi": int(r[1]),
        "pm25": str(r[2]),
        "waterRate": str(r[3]),
        "alarmCount": int(r[4])
    } for r in rows])


@app.route('/api/emission/rank')
def emission_rank():
    rows = hive_query("SELECT * FROM emission_rank ORDER BY aqi DESC LIMIT 8")
    return jsonify([{
        "id": int(r[0]),
        "name": r[1],
        "aqi": int(r[2]),
        "pm25": str(r[3]),
        "so2": str(r[4]),
        "no2": str(r[5]),
        "status": r[6]
    } for r in rows])


# ================================================================
# Scene 2: 污染扩散与管控
# ================================================================

@app.route('/api/pollution/factories')
def factories():
    rows = hive_query("SELECT * FROM factory_list")
    return jsonify([{"name": r[0], "lng": float(r[1]), "lat": float(r[2])} for r in rows])


@app.route('/api/pollution/control-compare')
def control_compare():
    rows = hive_query("SELECT label, predicted, controlled FROM control_compare_timeseries ORDER BY hour")
    predicted = []
    controlled = []
    labels = []
    for r in rows:
        labels.append(r[0])
        predicted.append(r[1])
        controlled.append(r[2])
    return jsonify({"predicted": predicted, "controlled": controlled, "labels": labels})


@app.route('/api/pollution/control-measures')
def control_measures():
    rows = hive_query("SELECT * FROM control_measures_status")
    return jsonify([{"name": r[0], "rate": int(r[1])} for r in rows])


@app.route('/api/pollution/reduction-rate')
def reduction_rate():
    rows = hive_query("SELECT * FROM emission_reduction_agg")
    if rows:
        return jsonify({"value": float(rows[0][0])})
    return jsonify({"value": 0})


# ================================================================
# Scene 3: 突发事件应急指挥
# ================================================================

@app.route('/api/emergency/incident')
def incident():
    rows = hive_query("SELECT * FROM active_incidents")
    if rows:
        return jsonify({"name": rows[0][0], "lng": float(rows[0][1]), "lat": float(rows[0][2])})
    return jsonify({})


@app.route('/api/emergency/rescue-teams')
def rescue_teams():
    rows = hive_query("SELECT * FROM rescue_teams_status")
    return jsonify([{
        "name": r[0], "lng": float(r[1]), "lat": float(r[2]), "eta": int(r[3])
    } for r in rows])


@app.route('/api/emergency/gantt')
def gantt():
    rows = hive_query("SELECT task, start_val, duration, dept, status FROM rescue_gantt_tasks ORDER BY start_val")
    return jsonify([{
        "task": r[0], "start": int(r[1]), "duration": int(r[2]),
        "dept": r[3], "status": r[4]
    } for r in rows])


@app.route('/api/emergency/impact-prediction')
def impact_prediction():
    rows = hive_query("SELECT time_val, area FROM impact_radius_prediction ORDER BY area")
    times = []
    areas = []
    for r in rows:
        times.append(r[0])
        areas.append(float(r[1]))
    return jsonify({"times": times, "areas": areas})


@app.route('/api/emergency/topology')
def topology():
    nodes_rows = hive_query("SELECT name, symbolSize, color, x, y FROM emergency_topology_nodes")
    links_rows = hive_query("SELECT source, target, color, type FROM emergency_topology_links")
    nodes = [{"name": r[0], "symbolSize": int(r[1]), "color": r[2], "x": int(r[3]), "y": int(r[4])} for r in nodes_rows]
    links = [{"source": r[0], "target": r[1], "color": r[2], "type": r[3]} for r in links_rows]
    return jsonify({"nodes": nodes, "links": links})


# ================================================================
# Scene 4: 流域水质与溯源分析
# ================================================================

@app.route('/api/water/river-sections')
def river_sections():
    rows = hive_query("SELECT name, lng, lat, quality, cod, nh3n, tp FROM river_section_realtime")
    return jsonify([{
        "name": r[0], "lng": float(r[1]), "lat": float(r[2]),
        "quality": r[3], "cod": float(r[4]), "nh3n": float(r[5]), "tp": float(r[6])
    } for r in rows])


@app.route('/api/water/sankey')
def sankey():
    nodes_rows = hive_query("SELECT name FROM sankey_nodes")
    links_rows = hive_query("SELECT source, target, value FROM sankey_links")
    nodes = [{"name": r[0]} for r in nodes_rows]
    links = [{"source": r[0], "target": r[1], "value": int(r[2])} for r in links_rows]
    return jsonify({"nodes": nodes, "links": links})


# ================================================================
# Scene 5: 资源配置与优化决策
# ================================================================

@app.route('/api/coverage/grid')
def coverage_grid():
    rows = hive_query("SELECT name, lng, lat, stationCount, popDensity, isBlindSpot FROM coverage_grid_analysis")
    return jsonify([{
        "name": r[0],
        "lng": float(r[1]),
        "lat": float(r[2]),
        "stationCount": int(r[3]),
        "popDensity": int(r[4]),
        "isBlindSpot": r[5].lower() == 'true'
    } for r in rows])


@app.route('/api/coverage/compare')
def coverage_compare():
    rows = hive_query("SELECT category, current_val, optimized FROM coverage_optimization_compare")
    categories = []
    current = []
    optimized = []
    for r in rows:
        categories.append(r[0])
        current.append(int(r[1]))
        optimized.append(int(r[2]))
    return jsonify({"categories": categories, "current": current, "optimized": optimized})


# ================================================================
# Health check
# ================================================================
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "database": HIVE_DB, "timestamp": datetime.now().isoformat()})


if __name__ == '__main__':
    print("=" * 60)
    print("  市域生态环境智慧监测感知大数据中枢 — API Server")
    print("  Database: Hive (environment)")
    print("  Port: 8080")
    print("  Endpoints: 20 REST APIs")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
