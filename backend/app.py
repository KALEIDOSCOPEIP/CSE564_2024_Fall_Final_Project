# backend/app.py
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

# 预加载数据
df = pd.read_csv("../Data/all_data.csv")

@app.route("/api/timeseries")
def timeseries():
    city = request.args.get("city")
    pollutant = request.args.get("type")
    
    sub = df[(df["city"] == city) & (df["type"] == pollutant)].copy()
    sub = sub.sort_values("date")
    result = sub[["date", "value"]].to_dict(orient="records")
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
