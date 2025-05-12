from flask import Blueprint, request, jsonify
from services import (
    get_timeseries,
    get_multi_city_timeseries,
    get_cities,
    get_monthly_city_values,
    get_province_info,
    get_province_pollutant_avg,
    get_sunburst_data,
    get_bubble_data
)

api = Blueprint('api', __name__)

@api.route("/api/timeseries")
def timeseries():
    city = request.args.get("city")
    pollutant = request.args.get("type")
    if not city or not pollutant:
        return jsonify({"error": "Missing parameters"}), 400
    return jsonify(get_timeseries(city, pollutant))

@api.route("/api/multi_city_timeseries")
def multi_city_timeseries():
    cities = request.args.getlist("cities")
    pollutant = request.args.get("type")
    if not cities or not pollutant:
        return jsonify({"error": "Missing parameters"}), 400
    return jsonify(get_multi_city_timeseries(cities, pollutant))

@api.route("/api/cities")
def cities():
    return jsonify(get_cities())

@api.route("/api/monthly_city_values")
def monthly_city_values():
    date = request.args.get("date")
    pollutant = request.args.get("type")
    if not date or not pollutant:
        return jsonify({"error": "Missing parameters"}), 400
    return jsonify(get_monthly_city_values(date, pollutant))

@api.route("/api/province_info")
def province_info():
    return jsonify(get_province_info())

@api.route('/api/province_pollutant_avg')
def province_pollutant_avg():
    pollutant = request.args.get("pollutant")
    year_start = request.args.get("start")
    year_end = request.args.get("end")
    if not pollutant or not year_start or not year_end:
        return jsonify({"error": "Missing parameters"}), 400
    return jsonify(get_province_pollutant_avg(pollutant, year_start, year_end))

@api.route("/api/sunburst-data")
def sunburst_data():
    return jsonify(get_sunburst_data())

@api.route("/api/bubble_data")
def bubble_data():
    return jsonify(get_bubble_data()) 