# 后端 API 接口规范

前端 DataService 会调用以下 REST API。你需要在本虚拟机上实现一个后端服务（Flask / Spring Boot / Node.js），查询 Hive 并以如下 JSON 格式返回数据。

**Base URL 配置**: 修改 `index.html` 第 243 行的 `API_BASE_URL` 和 `USE_MOCK`

```js
const API_BASE_URL = 'http://127.0.0.1:8080/api';  
const USE_MOCK = false;  // 改为 false 启用真实API
```

所有接口返回格式: `Content-Type: application/json`，状态码 200 表示成功。

---

## 接口总览

| DataService 方法 | API 路径 | 用途 |
|-----------------|----------|------|
| `getStationsRealtime()` | `/api/stations/realtime` | 50个监测站实时数据 → 地图散点 |
| `getKpiOverview()` | `/api/kpi/overview` | 3个翻牌器KPI |
| `getPollutionSources()` | `/api/pollution/sources` | 污染源饼图 |
| `getAirTrend()` | `/api/air/trend?hours=24` | 24h空气趋势面积图 |
| `getWaterTrend()` | `/api/water/trend?days=7` | 7天水质趋势面积图 |
| `getDistrictOverview()` | `/api/districts/overview` | 各区达标率柱状图 |
| `getEmissionRank()` | `/api/emission/rank` | 污染源排行 |
| `getFactories()` | `/api/pollution/factories` | 工厂位置 → 扩散图 |
| `getControlCompare()` | `/api/pollution/control-compare` | 管控对比双折线 |
| `getControlMeasures()` | `/api/pollution/control-measures` | 管控措施执行率 |
| `getReductionRate()` | `/api/pollution/reduction-rate` | 减排率仪表盘 |
| `getIncident()` | `/api/emergency/incident` | 事故点 |
| `getRescueTeams()` | `/api/emergency/rescue-teams` | 救援队位置+路线 |
| `getGanttData()` | `/api/emergency/gantt` | 救援甘特图 |
| `getImpactPrediction()` | `/api/emergency/impact-prediction` | 影响范围预测 |
| `getTopology()` | `/api/emergency/topology` | 应急拓扑图 |
| `getRiverSections()` | `/api/water/river-sections` | 河流断面水质 |
| `getSankeyData()` | `/api/water/sankey` | 桑基图 |
| `getCoverageGrid()` | `/api/coverage/grid` | 监测盲区气泡图 |
| `getCoverageCompare()` | `/api/coverage/compare` | 覆盖率柱状图+雷达图 |

---

## Scene 1: 全域环境态势一张图

### 1. GET /api/stations/realtime
所有监测站点的实时数据

```json
[
  {
    "id": 1,
    "name": "空气微站-01",
    "type": 0,
    "lng": 112.45,
    "lat": 33.52,
    "pm25": "45.2",
    "pm10": "78.5",
    "so2": "12.3",
    "no2": "35.6",
    "aqi": 68,
    "waterQuality": "II类",
    "cod": "15.2",
    "nh3n": "0.45",
    "status": "normal"
  }
]
```
| 字段 | 类型 | 说明 |
|------|------|------|
| type | int | 0=空气微站, 1=水质监测站, 2=重点排污企业, 3=噪声监测点, 4=辐射监测站 |
| status | string | "normal" 或 "alarm" |

### 2. GET /api/kpi/overview
顶部 KPI 指标

```json
{
  "airRate": 87.5,
  "waterRate": 92.1,
  "alarmCount": 3,
  "airTrend": 2.3,
  "waterTrend": 1.5,
  "alarmTrend": -2
}
```
airTrend/waterTrend/alarmTrend: 正数表示上升，负数表示下降。

### 3. GET /api/pollution/sources
污染源类型占比

```json
[
  { "name": "工业排放", "value": 38 },
  { "name": "机动车尾气", "value": 27 },
  { "name": "农业面源", "value": 15 },
  { "name": "生活源", "value": 12 },
  { "name": "建筑扬尘", "value": 8 }
]
```

### 4. GET /api/air/trend?hours=24
空气质量趋势 (时间序列)

```json
[
  { "time": "2026-06-09T06:00:00.000Z", "value": "55.30" },
  { "time": "2026-06-09T07:00:00.000Z", "value": "58.12" }
]
```

### 5. GET /api/water/trend?days=7
水质趋势 (时间序列)，每小时的 COD 值

```json
[
  { "time": "2026-06-02T00:00:00.000Z", "value": "3.15" },
  { "time": "2026-06-02T01:00:00.000Z", "value": "3.22" }
]
```

### 6. GET /api/districts/overview
各区环境概况

```json
[
  { "name": "城北区", "aqi": 55, "pm25": "32.5", "waterRate": "88.2", "alarmCount": 0 },
  { "name": "城东区", "aqi": 72, "pm25": "48.1", "waterRate": "85.0", "alarmCount": 1 }
]
```

### 7. GET /api/emission/rank
重点污染源排放排行 (取 top 8)

```json
[
  { "id": 21, "name": "重点排污企业-03", "aqi": 145, "pm25": "95.3", "so2": "42.1", "no2": "68.3", "status": "alarm" }
]
```

---

## Scene 2: 污染扩散与管控

### 8. GET /api/pollution/factories
重点工厂位置列表

```json
[
  { "name": "化工厂A", "lng": 112.62, "lat": 33.52 },
  { "name": "电厂B", "lng": 112.68, "lat": 33.58 }
]
```

### 9. GET /api/pollution/control-compare?hours=48
管控前后对比时序数据

```json
{
  "predicted": ["55", "60", "72", "88", "102", "115"],
  "controlled": ["55", "58", "65", "70", "68", "62"],
  "labels": ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00"]
}
```
predicted: 未管控预测值数组 (48个点)
controlled: 已管控实际值数组 (48个点)
labels: X轴标签数组 (48个)

### 10. GET /api/pollution/control-measures
管控措施执行率

```json
[
  { "name": "错峰生产", "rate": 85 },
  { "name": "道路洒水", "rate": 62 }
]
```

### 11. GET /api/pollution/reduction-rate
总体减排率

```json
{ "value": 42.5 }
```

---

## Scene 3: 突发事件应急指挥

### 12. GET /api/emergency/incident
当前事故信息

```json
{ "name": "化学品泄漏", "lng": 112.55, "lat": 33.5 }
```

### 13. GET /api/emergency/rescue-teams
救援队伍位置与预计到达时间

```json
[
  { "name": "市环保局应急队", "lng": 112.35, "lat": 33.42, "eta": 15 },
  { "name": "消防支队", "lng": 112.6, "lat": 33.55, "eta": 20 }
]
```
eta: 预计到达时间 (分钟)

### 14. GET /api/emergency/gantt
救援处置甘特图

```json
[
  { "task": "事故确认与报警", "start": 0, "duration": 5, "dept": "指挥中心", "status": "done" },
  { "task": "周边人员疏散", "start": 3, "duration": 25, "dept": "公安/消防", "status": "active" },
  { "task": "泄漏源封堵", "start": 8, "duration": 35, "dept": "消防支队", "status": "active" }
]
```
status: "done" | "active" | "pending"

### 15. GET /api/emergency/impact-prediction
影响范围预测

```json
{
  "times": ["0h", "1h", "2h", "3h", "4h", "5h", "6h"],
  "areas": [0, 2.5, 8.0, 18.5, 32.0, 45.0, 55.0]
}
```

### 16. GET /api/emergency/topology
应急资源网络拓扑

```json
{
  "nodes": [
    { "name": "事故点", "symbolSize": 40, "color": "#ff3355", "x": 300, "y": 200 },
    { "name": "环保局", "symbolSize": 28, "color": "#00d4ff", "x": 100, "y": 80 }
  ],
  "links": [
    { "source": "环保局", "target": "事故点", "color": "#00d4ff", "type": "solid" },
    { "source": "专家组", "target": "事故点", "color": "#ff9800", "type": "dashed" }
  ]
}
```
x/y: 力导向图的初始坐标 (0-600 范围)
type: "solid" 或 "dashed"

---

## Scene 4: 流域水质与溯源分析

### 17. GET /api/water/river-sections
河流断面监测数据

```json
[
  { "name": "上游断面A", "lng": 112.1, "lat": 33.18, "quality": "II类", "cod": 12.3, "nh3n": 0.35, "tp": 0.08 },
  { "name": "城区断面B", "lng": 112.35, "lat": 33.38, "quality": "III类", "cod": 18.7, "nh3n": 0.82, "tp": 0.15 }
]
```
quality: "I类" | "II类" | "III类" | "IV类" | "V类"

### 18. GET /api/water/sankey
污染源 → 断面 贡献桑基图

```json
{
  "nodes": [
    { "name": "工业废水" },
    { "name": "农业径流" },
    { "name": "上游断面A" }
  ],
  "links": [
    { "source": "工业废水", "target": "上游断面A", "value": 30 },
    { "source": "农业径流", "target": "上游断面A", "value": 12 }
  ]
}
```
source/target: 必须与 nodes 中的 name 完全匹配
value: 数值越大，线条越粗

---

## Scene 5: 资源配置与优化决策

### 19. GET /api/coverage/grid
网格覆盖数据 (6×6 = 36个网格)

```json
[
  { "name": "网格0-0", "lng": 112.125, "lat": 33.147, "stationCount": 3, "popDensity": 450, "isBlindSpot": false },
  { "name": "网格0-1", "lng": 112.125, "lat": 33.280, "stationCount": 1, "popDensity": 820, "isBlindSpot": true }
]
```
isBlindSpot: stationCount < 2 时为 true

### 20. GET /api/coverage/compare
覆盖率对比评估

```json
{
  "categories": ["空气监测", "水质监测", "噪声监测", "土壤监测", "辐射监测", "生态监测"],
  "current": [72, 65, 58, 45, 38, 55],
  "optimized": [91, 88, 82, 76, 70, 85]
}
```
current: 当前覆盖率百分比数组 (对应6个类别)
optimized: 优化方案覆盖率百分比数组

---

## Hive → API 实现建议

推荐的实现架构 (以 Python Flask 为例):

```
Hive 表 → PyHive/Impyla 查询 → Flask 路由 → JSON 响应 → 前端 ECharts
```

示例 (Flask):

```python
from flask import Flask, jsonify
from flask_cors import CORS
from pyhive import hive

app = Flask(__name__)
CORS(app)

conn = hive.Connection(host='localhost', port=10000, database='environment')

@app.route('/api/stations/realtime')
def stations_realtime():
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, type, lng, lat, pm25, pm10, so2, no2, aqi,
               water_quality, cod, nh3n, status
        FROM station_realtime_agg
    ''')
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return jsonify(rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

前端 `index.html` 中的配置:
```js
const API_BASE_URL = 'http://192.168.1.100:8080/api';  // VM IP
const USE_MOCK = false;
```
