# backend/app.py
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

# 预加载数据
all_data = pd.read_csv("../Data/all_data.csv")
extras = pd.read_csv("../Data/Extras.csv")

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


if __name__ == "__main__":
    app.run(debug=True)
