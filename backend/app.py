# backend/app.py
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

# 预加载数据
all_data = pd.read_csv("../Data/merged_all_data_en.csv")
all_years = all_data['date'].astype(str).str[:4]
# extras = pd.read_csv("../Data/Extras.csv")
bubble_df = pd.read_csv("../Data/bubble_data_full_en.csv")

@app.route("/api/timeseries")
def timeseries():
    city = request.args.get("city")
    pollutant = request.args.get("type")
    
    sub = all_data[(all_data["city"] == city) & (all_data["type"] == pollutant)].copy()
    sub = sub.sort_values("date")
    result = sub[["date", "value"]].to_dict(orient="records")
    return jsonify(result)

@app.route("/api/multi_city_timeseries")
def multi_city_timeseries():
    cities = request.args.getlist("cities")
    pollutant = request.args.get("type")

    sub = all_data[(all_data["city"].isin(cities)) & (all_data["type"] == pollutant)].copy()
    sub = sub.sort_values(["city", "date"])
    
    result = sub[["city", "date", "value"]].to_dict(orient="records")
    return jsonify(result)

@app.route("/api/cities")
def get_cities():
    cities = all_data["city"].dropna().unique().tolist()
    cities.sort()
    return jsonify(cities)

@app.route("/api/monthly_city_values")
def monthly_city_values():
    # date = request.args.get("date")
    # pollutant = request.args.get("type")
    # sub = all_data[(all_data["date"] == date) & (all_data["type"] == pollutant)].copy()
    # sub = sub.sort_values("value", ascending=False)
    # result = sub[["city", "value"]].to_dict(orient="records")
    # return jsonify(result)
    # print(all_data.dtypes)

    date = int(request.args.get("date"))
    pollutant = request.args.get("type")

    sub = all_data[(all_data["date"] == date) & (all_data["type"] == pollutant)].copy()
    sub = sub.dropna(subset=["province"])
    
    grouped = sub.groupby("province")["value"].mean().reset_index()
    grouped.columns = ["name", "value"]
    grouped["value"] = grouped["value"].round(2)
    return jsonify(grouped.to_dict(orient="records"))


# 生成每个省的统计信息
def get_province_data():
    # 将城市按省份分组，统计人口总和与 GDP 总和
    df = all_data.copy()
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df["gdp"] = pd.to_numeric(df["gdp"], errors="coerce")
    df["is_coastal"] = df["is_coastal"].replace({"是": "Yes", "否": "No"})
    grouped = df.groupby("province").agg({
        "population": "sum",
        "gdp": "sum",
        "region": "first",
        "is_coastal": "first",
        "climate_type": "first",
    }).reset_index()
    # grouped = pd.DataFrame(df.groupby("province"))
    grouped["population"] = (grouped["population"] / 1e9).round(2)
    grouped['gdp'] = (grouped['gdp'] / 1000).round(2)

    # 转为前端用格式
    grouped = grouped.fillna(0)
    result = grouped.to_dict(orient="records")
    # print(result)
    return result

@app.route("/api/province_info")
def province_info():
    data = get_province_data()
    return jsonify(data)

@app.route('/api/province_pollutant_avg')
def province_pollutant_avg():
    pollutant = request.args.get("pollutant")
    year_start = int(request.args.get("start"))
    year_end = int(request.args.get("end"))
    print(type(all_data['date'][0]))

    if pollutant is None:
        return jsonify({"error": "Missing pollutant"}), 400

    # 过滤污染类型 & 年份
    sub = all_data[(all_data['type'] == pollutant) &
                   (all_years.astype(int) >= year_start) &
                   (all_years.astype(int) <= year_end)].copy()

    # 合并省份
    merged = sub.merge(all_data, on='city', how='left')
    merged = merged.dropna(subset=['province'])

    # 每省计算平均值
    grouped = merged.groupby('province').agg({
        'value': 'mean',
        'population': 'sum',
        'gdp': 'sum',
        'region': 'first'
    }).reset_index()

    grouped = grouped.rename(columns={
        'value': 'avg_value'
    })

    grouped = grouped.fillna(0)
    return jsonify(grouped.to_dict(orient='records'))


@app.route("/api/sunburst-data")
def get_sunburst_data():
    df = all_data.dropna(subset=["type", "province", "value"])

    # 构建旭日图结构
    result = {"name": "Nation", "children": []}
    for pollutant in df["type"].unique():
        sub_df = df[df["type"] == pollutant]
        province_max = (
            sub_df.groupby("province")["value"]
            .max()
            .reset_index()
            .sort_values("value", ascending=False)
            .head(5)
        )
        result["children"].append({
            "name": pollutant,
            "children": [
                {"name": row["province"], "value": round(row["value"], 2)}
                for _, row in province_max.iterrows()
            ]
        })

    return jsonify(result)

@app.route("/api/bubble_data")
def get_bubble_data():
    data = bubble_df.fillna(0).to_dict(orient="records")
    return jsonify(data)


@app.route('/api/parallel-data')
def get_parallel_data():
    pollutant = request.args.get('type', 'PM2.5')
    # start = int(request.args.get('start', '2014-05'))
    start = int(request.args.get('start', '201405').replace('-', ''))
    end = int(request.args.get('end', '202503').replace('-', ''))
    # end = int(request.args.get('end', '2025-03'))

    start = start if start >= 201405 else 201405
    end = end if end <= 202503 else 202503
    if start > end:
        start, end = end, start
    
    # df_filtered = all_data[(all_data['type'] == pollutant) & 
    #                    (all_data['date'] >= start) & 
    #                    (all_data['date'] <= end)]
    # year_months = bubble_df['year_month'].astype(str).replace('-', '').astype(int)
    year_months = bubble_df['year_month'].apply(lambda x: int(x.replace('-', '')))
    df_filtered = bubble_df[ 
                       (year_months >= start) & 
                       (year_months <= end)]

    grouped = df_filtered.groupby('province').agg({
        # 'value': 'mean',
        'population': 'first',
        'gdp': 'first',
        'is_coastal': 'first',
        'climate_type': 'first',

        'AQI': 'mean',
        'CO': 'mean',
        'NO2': 'mean',
        'O3': 'mean',
        'PM10': 'mean',
        'PM2.5': 'mean',
        'SO2': 'mean',
    }).reset_index()

    # 映射是否沿海为数值
    coastal_mapping = {'Yes': 1, 'No': 0}
    grouped['is_coastal'] = grouped['is_coastal'].map(coastal_mapping)
    print(grouped['is_coastal'])

    # 映射气候类型为数值
    climate_mapping = {name: i for i, name in enumerate(grouped['climate_type'].unique())}
    grouped['climate_code'] = grouped['climate_type'].map(climate_mapping)

    # 归一化数值字段
    # for col in ['value', 'population', 'gdp']:
    #     grouped[col] = (grouped[col] - grouped[col].min()) / (grouped[col].max() - grouped[col].min())
    # for col in ['AQI', 'CO', 'NO2', 'O3', 'PM10', 'PM2.5', 'SO2', ]:
    #     grouped[col] = (grouped[col] - grouped[col].min()) / (grouped[col].max() - grouped[col].min())

    result = grouped[['province',
                    #    'value',
                         'population',
                           'gdp',
                             'is_coastal',
                               'climate_code',
                               'AQI',
                               'CO',
                               'NO2',
                               'O3',
                               'PM10',
                               'PM2.5',
                               'SO2']].to_dict(orient='records')
    return jsonify(result)


@app.route("/api/radar-data")
def radar_data():
    cities = request.args.get("cities", "").split(",")
    pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
    result = []
    max_value = 0

    for city in cities:
        values = []
        for p in pollutants:
            v = all_data[(all_data['city'] == city) & (all_data['type'] == p)]['value'].mean()
            values.append(round(v, 2) if pd.notna(v) else 0)
            max_value = max(max_value, v if pd.notna(v) else 0)
        result.append({"city": city, "values": values})

    return jsonify({
        "pollutants": pollutants,
        "series": result,
        "maxValue": round(max_value * 1.2, 1)  # 稍大于最大值以避免贴边
    })


if __name__ == "__main__":
    app.run(debug=True)
