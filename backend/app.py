# backend/app.py
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

# 预加载数据
all_data = pd.read_csv("../Data/merged_all_data.csv")
all_years = all_data['date'].astype(str).str[:4]
# extras = pd.read_csv("../Data/Extras.csv")

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
    grouped = df.groupby("province").agg({
        "population": "sum",
        "gdp": "sum"
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
    result = {"name": "全国", "children": []}
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


if __name__ == "__main__":
    app.run(debug=True)
