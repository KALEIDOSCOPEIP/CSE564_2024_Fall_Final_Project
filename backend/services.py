import pandas as pd
from typing import List, Dict, Any

def _load_all_data() -> pd.DataFrame:
    return pd.read_csv("../Data/merged_all_data.csv")

def _load_bubble_data() -> pd.DataFrame:
    return pd.read_csv("../Data/bubble_data_full.csv")

all_data = _load_all_data()
all_years = all_data['date'].astype(str).str[:4]

# --- Service Functions ---
def get_timeseries(city: str, pollutant: str) -> List[Dict[str, Any]]:
    """Return time series for a city and pollutant."""
    sub = all_data[(all_data["city"] == city) & (all_data["type"] == pollutant)].copy()
    sub = sub.sort_values("date")
    return sub[["date", "value"]].to_dict(orient="records")

def get_multi_city_timeseries(cities: List[str], pollutant: str) -> List[Dict[str, Any]]:
    """Return time series for multiple cities and a pollutant."""
    sub = all_data[(all_data["city"].isin(cities)) & (all_data["type"] == pollutant)].copy()
    sub = sub.sort_values(["city", "date"])
    return sub[["city", "date", "value"]].to_dict(orient="records")

def get_cities() -> List[str]:
    """Return sorted list of unique cities."""
    cities = all_data["city"].dropna().unique().tolist()
    cities.sort()
    return cities

def get_monthly_city_values(date: str, pollutant: str) -> List[Dict[str, Any]]:
    """Return average pollutant value per province for a given month."""
    date = int(date)
    sub = all_data[(all_data["date"] == date) & (all_data["type"] == pollutant)].copy()
    sub = sub.dropna(subset=["province"])
    grouped = sub.groupby("province")["value"].mean().reset_index()
    grouped.columns = ["name", "value"]
    grouped["value"] = grouped["value"].round(2)
    return grouped.to_dict(orient="records")

def get_province_info() -> List[Dict[str, Any]]:
    """Return population and GDP info per province."""
    df = all_data.copy()
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df["gdp"] = pd.to_numeric(df["gdp"], errors="coerce")
    grouped = df.groupby("province").agg({
        "population": "sum",
        "gdp": "sum"
    }).reset_index()
    grouped["population"] = (grouped["population"] / 1e9).round(2)
    grouped['gdp'] = (grouped['gdp'] / 1000).round(2)
    grouped = grouped.fillna(0)
    return grouped.to_dict(orient="records")

def get_province_pollutant_avg(pollutant: str, year_start: str, year_end: str) -> List[Dict[str, Any]]:
    """Return average pollutant value per province for a year range."""
    year_start = int(year_start)
    year_end = int(year_end)
    sub = all_data[(all_data['type'] == pollutant) &
                   (all_years.astype(int) >= year_start) &
                   (all_years.astype(int) <= year_end)].copy()
    merged = sub.merge(all_data, on='city', how='left')
    merged = merged.dropna(subset=['province'])
    grouped = merged.groupby('province').agg({
        'value': 'mean',
        'population': 'sum',
        'gdp': 'sum',
        'region': 'first'
    }).reset_index()
    grouped = grouped.rename(columns={'value': 'avg_value'})
    grouped = grouped.fillna(0)
    return grouped.to_dict(orient='records')

def get_sunburst_data() -> Dict[str, Any]:
    """Return data for sunburst chart."""
    df = all_data.dropna(subset=["type", "province", "value"])
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
    return result

def get_bubble_data() -> List[Dict[str, Any]]:
    """Return bubble chart data."""
    bubble_df = _load_bubble_data()
    data = bubble_df.fillna(0).to_dict(orient="records")
    return data 