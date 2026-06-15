#!/usr/bin/env python3
"""
生成市域生态环境智慧监测感知大数据中枢 模拟数据集
总计 50,000+ 条记录，涵盖所有 API 接口所需数据
城市: 江城 (坐标中心 112.52, 33.48)
"""
import csv
import math
import random
import os
from datetime import datetime, timedelta

random.seed(42)
OUTPUT_DIR = "/home/wonseok/tmp/csv_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

NOW = datetime(2026, 6, 13, 14, 30, 0)
DAYS = 90  # 90天历史数据
HOURS_PER_DAY = 24

# =====================================================
# 城市地理参数
# =====================================================
CENTER_LNG, CENTER_LAT = 112.52, 33.48
LNG_RANGE = (111.95, 112.95)
LAT_RANGE = (33.05, 33.85)

# 六个区
DISTRICTS = ['城北区', '城东区', '城南区', '城西区', '中心区', '高新区']
DISTRICT_BOUNDS = {
    '城北区': {'lng': (112.1, 112.85), 'lat': (33.5, 33.82)},
    '城东区': {'lng': (112.45, 112.92), 'lat': (33.3, 33.6)},
    '城南区': {'lng': (111.98, 112.7), 'lat': (33.1, 33.42)},
    '城西区': {'lng': (112.0, 112.35), 'lat': (33.1, 33.35)},
    '中心区': {'lng': (112.2, 112.6), 'lat': (33.32, 33.55)},
    '高新区': {'lng': (112.55, 112.88), 'lat': (33.45, 33.75)},
}

# =====================================================
# 50个监测站点定义
# =====================================================
STATION_TYPES = {
    0: '空气微站',
    1: '水质监测站',
    2: '重点排污企业',
    3: '噪声监测点',
    4: '辐射监测站'
}

def gen_stations():
    """生成50个监测站"""
    stations = []
    idx = 1
    # 空气微站 15个 (type=0)
    for i in range(15):
        stations.append({
            'id': idx, 'name': f'空气微站-{i+1:02d}', 'type': 0,
            'lng': round(112.52 + (random.random()-0.5)*0.7, 5),
            'lat': round(33.48 + (random.random()-0.5)*0.6, 5),
        })
        idx += 1
    # 水质监测站 13个 (type=1)
    for i in range(13):
        stations.append({
            'id': idx, 'name': f'水质监测站-{i+1:02d}', 'type': 1,
            'lng': round(112.52 + (random.random()-0.5)*0.7, 5),
            'lat': round(33.48 + (random.random()-0.5)*0.6, 5),
        })
        idx += 1
    # 重点排污企业 10个 (type=2)
    for i in range(10):
        stations.append({
            'id': idx, 'name': f'重点排污企业-{i+1:02d}', 'type': 2,
            'lng': round(112.52 + (random.random()-0.5)*0.7, 5),
            'lat': round(33.48 + (random.random()-0.5)*0.6, 5),
        })
        idx += 1
    # 噪声监测点 6个 (type=3)
    for i in range(6):
        stations.append({
            'id': idx, 'name': f'噪声监测点-{i+1:02d}', 'type': 3,
            'lng': round(112.52 + (random.random()-0.5)*0.7, 5),
            'lat': round(33.48 + (random.random()-0.5)*0.6, 5),
        })
        idx += 1
    # 辐射监测站 6个 (type=4)
    for i in range(6):
        stations.append({
            'id': idx, 'name': f'辐射监测站-{i+1:02d}', 'type': 4,
            'lng': round(112.52 + (random.random()-0.5)*0.7, 5),
            'lat': round(33.48 + (random.random()-0.5)*0.6, 5),
        })
        idx += 1
    return stations

STATIONS = gen_stations()
AIR_STATIONS = [s for s in STATIONS if s['type'] == 0]     # 15
WATER_STATIONS = [s for s in STATIONS if s['type'] == 1]   # 13
FACTORY_STATIONS = [s for s in STATIONS if s['type'] == 2] # 10

# =====================================================
# 数据生成辅助函数
# =====================================================
def daily_pattern(hour, base, amplitude):
    """模拟日周期波动: 早晚高峰高, 中午低"""
    morning_peak = 10 * math.exp(-((hour-8)**2)/8)
    evening_peak = 8 * math.exp(-((hour-19)**2)/8)
    return base + amplitude * (morning_peak + evening_peak) / 18

def seasonal_pattern(day_of_year, base, amplitude):
    """模拟季节性波动 (冬季高, 夏季低)"""
    return base + amplitude * math.sin((day_of_year - 15) * 2 * math.pi / 365)

def noise(factor=1.0):
    return (random.random() - 0.5) * factor

def ensure_positive(v):
    return max(0.01, v)

# =====================================================
# 1. station_realtime_agg.csv (50行)
# =====================================================
def gen_station_realtime():
    rows = []
    for s in STATIONS:
        sid = s['id']
        aqi_base = 55 if s['type'] == 0 else (75 if s['type'] == 2 else 45)
        aqi = int(aqi_base + noise(60))
        aqi = max(15, min(200, aqi))
        pm25_val = round(aqi * 0.65 + noise(10), 1)
        pm10_val = round(pm25_val * 1.6 + noise(15), 1)
        so2_val = round(8 + abs(noise(18)), 1)
        no2_val = round(18 + abs(noise(28)), 1)
        water_qualities = ['I类', 'II类', 'III类', 'IV类', 'V类']
        wq_weights = [0.05, 0.25, 0.35, 0.25, 0.10] if s['type'] in [1,2] else [0.15, 0.35, 0.30, 0.15, 0.05]
        water_q = random.choices(water_qualities, weights=wq_weights, k=1)[0]
        cod_val = round(6 + noise(20), 1) if water_q == 'I类' else round(12 + noise(35), 1)
        nh3n_val = round(0.1 + abs(noise(1.2)), 2)
        status = 'alarm' if random.random() < 0.12 else 'normal'
        rows.append({
            'id': sid, 'name': s['name'], 'type': s['type'],
            'lng': s['lng'], 'lat': s['lat'],
            'pm25': pm25_val, 'pm10': pm10_val, 'so2': so2_val, 'no2': no2_val,
            'aqi': aqi, 'waterQuality': water_q, 'cod': cod_val, 'nh3n': nh3n_val,
            'status': status
        })
    return rows

# =====================================================
# 2. kpi_daily_agg.csv (1行)
# =====================================================
def gen_kpi_overview():
    return [{
        'airRate': round(80 + noise(12), 1),
        'waterRate': round(85 + noise(12), 1),
        'alarmCount': random.randint(1, 5),
        'airTrend': round(noise(6), 1),
        'waterTrend': round(noise(4), 1),
        'alarmTrend': random.randint(-5, 3)
    }]

# =====================================================
# 3. pollution_source_agg.csv (5行)
# =====================================================
def gen_pollution_sources():
    items = [
        ('工业排放', 38), ('机动车尾气', 27), ('农业面源', 15),
        ('生活源', 12), ('建筑扬尘', 8)
    ]
    return [{'name': n, 'value': round(v + noise(4), 1)} for n, v in items]

# =====================================================
# 4. air_quality_timeseries.csv (~64,800行)
# 30个空气监测站 × 90天 × 24小时
# =====================================================
def gen_air_timeseries():
    rows = []
    # Use air stations (type=0) + some water/factory stations as monitoring points
    ts_stations = STATIONS[:30]  # First 30 stations
    for hour_offset in range(DAYS * HOURS_PER_DAY):
        ts = NOW - timedelta(hours=hour_offset)
        day_of_year = ts.timetuple().tm_yday
        hour = ts.hour
        for s in ts_stations:
            base_pm = 50 + (s['lng'] - CENTER_LNG) * 30 + (s['lat'] - CENTER_LAT) * 20
            base_pm += seasonal_pattern(day_of_year, 0, 25)
            base_pm += daily_pattern(hour, 0, 20)
            value = round(base_pm + noise(15), 2)
            value = ensure_positive(value)
            rows.append({
                'station_id': s['id'],
                'time': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'value': f'{value:.2f}'
            })
    return rows

# =====================================================
# 5. water_quality_timeseries.csv (~21,600行)
# 10个水质监测站 × 90天 × 24小时
# =====================================================
def gen_water_timeseries():
    rows = []
    ts_stations = WATER_STATIONS[:10]
    for hour_offset in range(DAYS * HOURS_PER_DAY):
        ts = NOW - timedelta(hours=hour_offset)
        day_of_year = ts.timetuple().tm_yday
        hour = ts.hour
        for s in ts_stations:
            base_cod = 15 + (s['lng'] - CENTER_LNG) * 15
            base_cod += seasonal_pattern(day_of_year, 0, 5)
            base_cod += daily_pattern(hour, 0, 2)
            value = round(base_cod + noise(3), 2)
            value = ensure_positive(value)
            rows.append({
                'station_id': s['id'],
                'time': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'value': f'{value:.2f}'
            })
    return rows

# =====================================================
# 6. district_overview.csv (6行)
# =====================================================
def gen_district_overview():
    rows = []
    for d in DISTRICTS:
        rows.append({
            'name': d,
            'aqi': random.randint(35, 120),
            'pm25': round(20 + random.random() * 55, 1),
            'waterRate': round(78 + random.random() * 22, 1),
            'alarmCount': random.randint(0, 5)
        })
    return rows

# =====================================================
# 7. emission_rank.csv (10行 — 对应重点排污企业)
# =====================================================
def gen_emission_rank():
    rows = []
    for s in FACTORY_STATIONS:
        aqi = random.randint(80, 200)
        rows.append({
            'id': s['id'],
            'name': s['name'],
            'aqi': aqi,
            'pm25': round(aqi * 0.65 + noise(8), 1),
            'so2': round(15 + abs(noise(35)), 1),
            'no2': round(25 + abs(noise(50)), 1),
            'status': 'alarm' if aqi > 130 else 'normal'
        })
    rows.sort(key=lambda x: x['aqi'], reverse=True)
    return rows

# =====================================================
# 8. factory_list.csv (4行)
# =====================================================
def gen_factories():
    return [
        {'name': '化工厂A', 'lng': 112.62, 'lat': 33.52},
        {'name': '电厂B', 'lng': 112.68, 'lat': 33.58},
        {'name': '钢铁厂C', 'lng': 112.70, 'lat': 33.50},
        {'name': '制药厂D', 'lng': 112.64, 'lat': 33.60},
    ]

# =====================================================
# 9. control_compare_timeseries.csv (48行)
# =====================================================
def gen_control_compare():
    rows = []
    for h in range(48):
        predicted = round(50 + 80 * (1 - math.exp(-h/10)) + noise(10), 0)
        base_ctrl = 50 + 80 * (1 - math.exp(-h/10))
        controlled = base_ctrl if h < 10 else round(base_ctrl * (1 - 0.4 * (1 - math.exp(-(h-10)/8))) + noise(8), 0)
        rows.append({
            'hour': h,
            'label': f'{h:02d}:00',
            'predicted': str(int(predicted)),
            'controlled': str(int(controlled))
        })
    return rows

# =====================================================
# 10. control_measures_status.csv (5行)
# =====================================================
def gen_control_measures():
    return [
        {'name': '错峰生产', 'rate': random.randint(80, 95)},
        {'name': '道路洒水', 'rate': random.randint(55, 75)},
        {'name': '工地停工', 'rate': random.randint(70, 88)},
        {'name': '车辆限行', 'rate': random.randint(50, 65)},
        {'name': '绿电替代', 'rate': random.randint(65, 80)},
    ]

# =====================================================
# 11. emission_reduction_agg.csv (1行)
# =====================================================
def gen_reduction_rate():
    return [{'value': round(35 + random.random() * 15, 1)}]

# =====================================================
# 12. active_incidents.csv (1行)
# =====================================================
def gen_incident():
    return [{'name': '化学品泄漏', 'lng': 112.55, 'lat': 33.50}]

# =====================================================
# 13. rescue_teams_status.csv (6行)
# =====================================================
def gen_rescue_teams():
    return [
        {'name': '市环保局应急队', 'lng': 112.35, 'lat': 33.42, 'eta': 15},
        {'name': '消防支队', 'lng': 112.60, 'lat': 33.55, 'eta': 20},
        {'name': '医疗救援队', 'lng': 112.40, 'lat': 33.60, 'eta': 25},
        {'name': '省级专家组', 'lng': 112.70, 'lat': 33.30, 'eta': 45},
        {'name': '物资储备库A', 'lng': 112.20, 'lat': 33.50, 'eta': 30},
        {'name': '物资储备库B', 'lng': 112.55, 'lat': 33.70, 'eta': 18},
    ]

# =====================================================
# 14. rescue_gantt_tasks.csv (7行)
# =====================================================
def gen_gantt():
    return [
        {'task': '事故确认与报警', 'start': 0, 'duration': 5, 'dept': '指挥中心', 'status': 'done'},
        {'task': '周边人员疏散', 'start': 3, 'duration': 25, 'dept': '公安/消防', 'status': 'active'},
        {'task': '泄漏源封堵', 'start': 8, 'duration': 35, 'dept': '消防支队', 'status': 'active'},
        {'task': '环境应急监测', 'start': 5, 'duration': 40, 'dept': '环保局', 'status': 'active'},
        {'task': '医疗救治', 'start': 10, 'duration': 30, 'dept': '卫健委', 'status': 'pending'},
        {'task': '污染扩散控制', 'start': 15, 'duration': 45, 'dept': '环保局+消防', 'status': 'pending'},
        {'task': '善后处置与评估', 'start': 40, 'duration': 60, 'dept': '多部门联合', 'status': 'pending'},
    ]

# =====================================================
# 15. impact_radius_prediction.csv (7行)
# =====================================================
def gen_impact():
    times = ['0h', '1h', '2h', '3h', '4h', '5h', '6h']
    areas = [0, 2.5, 8.0, 18.5, 32.0, 45.0, 55.0]
    return [{'time': t, 'area': a} for t, a in zip(times, areas)]

# =====================================================
# 16. emergency_topology_nodes.csv + links.csv
# =====================================================
def gen_topology():
    nodes = [
        {'name': '事故点', 'symbolSize': 40, 'color': '#ff3355', 'x': 300, 'y': 200},
        {'name': '环保局', 'symbolSize': 28, 'color': '#00d4ff', 'x': 100, 'y': 80},
        {'name': '消防支队', 'symbolSize': 28, 'color': '#00d4ff', 'x': 100, 'y': 200},
        {'name': '医疗队', 'symbolSize': 28, 'color': '#00d4ff', 'x': 100, 'y': 320},
        {'name': '专家组', 'symbolSize': 28, 'color': '#00d4ff', 'x': 300, 'y': 50},
        {'name': '物资库A', 'symbolSize': 30, 'color': '#ff9800', 'x': 500, 'y': 120},
        {'name': '物资库B', 'symbolSize': 30, 'color': '#ff9800', 'x': 500, 'y': 280},
    ]
    links = [
        {'source': '环保局', 'target': '事故点', 'color': '#00d4ff', 'type': 'solid'},
        {'source': '消防支队', 'target': '事故点', 'color': '#00ff88', 'type': 'solid'},
        {'source': '医疗队', 'target': '事故点', 'color': '#e040fb', 'type': 'solid'},
        {'source': '专家组', 'target': '事故点', 'color': '#ff9800', 'type': 'solid'},
        {'source': '物资库A', 'target': '事故点', 'color': '#ff9800', 'type': 'solid'},
        {'source': '物资库B', 'target': '事故点', 'color': '#ff9800', 'type': 'solid'},
        {'source': '环保局', 'target': '专家组', 'color': '#667788', 'type': 'dashed'},
    ]
    return nodes, links

# =====================================================
# 17. river_section_realtime.csv (5行)
# =====================================================
def gen_river_sections():
    return [
        {'name': '上游断面A', 'lng': 112.10, 'lat': 33.18, 'quality': 'II类', 'cod': 12.3, 'nh3n': 0.35, 'tp': 0.08},
        {'name': '城区断面B', 'lng': 112.35, 'lat': 33.38, 'quality': 'III类', 'cod': 18.7, 'nh3n': 0.82, 'tp': 0.15},
        {'name': '工业区断面C', 'lng': 112.55, 'lat': 33.52, 'quality': 'IV类', 'cod': 28.4, 'nh3n': 1.56, 'tp': 0.28},
        {'name': '下游断面D', 'lng': 112.78, 'lat': 33.68, 'quality': 'III类', 'cod': 20.1, 'nh3n': 0.95, 'tp': 0.18},
        {'name': '北支流断面E', 'lng': 112.38, 'lat': 33.58, 'quality': 'II类', 'cod': 10.5, 'nh3n': 0.28, 'tp': 0.06},
    ]

# =====================================================
# 18. sankey_nodes.csv + sankey_links.csv
# =====================================================
def gen_sankey():
    nodes = [
        {'name': '工业废水'},
        {'name': '农业径流'},
        {'name': '生活污水'},
        {'name': '畜禽养殖'},
        {'name': '城市径流'},
        {'name': '上游断面A'},
        {'name': '城区断面B'},
        {'name': '工业区断面C'},
        {'name': '下游断面D'},
        {'name': '北支流断面E'},
    ]
    links = [
        {'source': '工业废水', 'target': '工业区断面C', 'value': 45},
        {'source': '工业废水', 'target': '城区断面B', 'value': 18},
        {'source': '工业废水', 'target': '下游断面D', 'value': 12},
        {'source': '农业径流', 'target': '上游断面A', 'value': 30},
        {'source': '农业径流', 'target': '北支流断面E', 'value': 25},
        {'source': '农业径流', 'target': '城区断面B', 'value': 10},
        {'source': '生活污水', 'target': '城区断面B', 'value': 35},
        {'source': '生活污水', 'target': '下游断面D', 'value': 20},
        {'source': '畜禽养殖', 'target': '北支流断面E', 'value': 15},
        {'source': '畜禽养殖', 'target': '上游断面A', 'value': 8},
        {'source': '畜禽养殖', 'target': '工业区断面C', 'value': 7},
        {'source': '城市径流', 'target': '城区断面B', 'value': 22},
        {'source': '城市径流', 'target': '下游断面D', 'value': 14},
    ]
    return nodes, links

# =====================================================
# 19. coverage_grid_analysis.csv (36行, 6×6网格)
# =====================================================
def gen_coverage_grid():
    rows = []
    for i in range(6):
        for j in range(6):
            lng = round(112.05 + (i + 0.5) * 0.9 / 6, 5)
            lat = round(33.08 + (j + 0.5) * 0.8 / 6, 5)
            cnt = sum(1 for s in STATIONS if abs(s['lng'] - lng) < 0.15 and abs(s['lat'] - lat) < 0.12)
            pop = random.randint(100, 950)
            rows.append({
                'name': f'网格{i}-{j}',
                'lng': lng, 'lat': lat,
                'stationCount': cnt,
                'popDensity': pop,
                'isBlindSpot': 'true' if cnt < 2 else 'false'
            })
    return rows

# =====================================================
# 20. coverage_optimization_compare.csv (6行)
# =====================================================
def gen_coverage_compare():
    return [
        {'category': '空气监测', 'current': 72, 'optimized': 91},
        {'category': '水质监测', 'current': 65, 'optimized': 88},
        {'category': '噪声监测', 'current': 58, 'optimized': 82},
        {'category': '土壤监测', 'current': 45, 'optimized': 76},
        {'category': '辐射监测', 'current': 38, 'optimized': 70},
        {'category': '生态监测', 'current': 55, 'optimized': 85},
    ]

# =====================================================
# CSV 写入
# =====================================================
def write_csv(filename, rows, fieldnames):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f'  ✓ {filename}: {len(rows)} 行')
    return len(rows)

def main():
    print('生成模拟数据...')
    total = 0

    total += write_csv('station_realtime_agg.csv', gen_station_realtime(),
                       ['id','name','type','lng','lat','pm25','pm10','so2','no2','aqi','waterQuality','cod','nh3n','status'])

    total += write_csv('kpi_daily_agg.csv', gen_kpi_overview(),
                       ['airRate','waterRate','alarmCount','airTrend','waterTrend','alarmTrend'])

    total += write_csv('pollution_source_agg.csv', gen_pollution_sources(),
                       ['name','value'])

    air_ts = gen_air_timeseries()
    total += write_csv('air_quality_timeseries.csv', air_ts,
                       ['station_id','time','value'])

    water_ts = gen_water_timeseries()
    total += write_csv('water_quality_timeseries.csv', water_ts,
                       ['station_id','time','value'])

    total += write_csv('district_overview.csv', gen_district_overview(),
                       ['name','aqi','pm25','waterRate','alarmCount'])

    total += write_csv('emission_rank.csv', gen_emission_rank(),
                       ['id','name','aqi','pm25','so2','no2','status'])

    total += write_csv('factory_list.csv', gen_factories(),
                       ['name','lng','lat'])

    total += write_csv('control_compare_timeseries.csv', gen_control_compare(),
                       ['hour','label','predicted','controlled'])

    total += write_csv('control_measures_status.csv', gen_control_measures(),
                       ['name','rate'])

    total += write_csv('emission_reduction_agg.csv', gen_reduction_rate(),
                       ['value'])

    total += write_csv('active_incidents.csv', gen_incident(),
                       ['name','lng','lat'])

    total += write_csv('rescue_teams_status.csv', gen_rescue_teams(),
                       ['name','lng','lat','eta'])

    total += write_csv('rescue_gantt_tasks.csv', gen_gantt(),
                       ['task','start','duration','dept','status'])

    total += write_csv('impact_radius_prediction.csv', gen_impact(),
                       ['time','area'])

    nodes, links = gen_topology()
    total += write_csv('emergency_topology_nodes.csv', nodes,
                       ['name','symbolSize','color','x','y'])
    total += write_csv('emergency_topology_links.csv', links,
                       ['source','target','color','type'])

    total += write_csv('river_section_realtime.csv', gen_river_sections(),
                       ['name','lng','lat','quality','cod','nh3n','tp'])

    snodes, slinks = gen_sankey()
    total += write_csv('sankey_nodes.csv', snodes, ['name'])
    total += write_csv('sankey_links.csv', slinks, ['source','target','value'])

    total += write_csv('coverage_grid_analysis.csv', gen_coverage_grid(),
                       ['name','lng','lat','stationCount','popDensity','isBlindSpot'])

    total += write_csv('coverage_optimization_compare.csv', gen_coverage_compare(),
                       ['category','current','optimized'])

    print(f'\n总计: {total} 条记录 (需求: ≥50,000)')
    if total >= 50000:
        print('✅ 数据量达标!')
    else:
        print(f'❌ 数据量不足, 还差 {50000 - total} 条')

if __name__ == '__main__':
    main()
