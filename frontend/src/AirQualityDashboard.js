// 多城市空气质量趋势图（压缩折线图区域尺寸）
import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import Select from "react-select";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const COLORS = [
  "#3366CC", "#DC3912", "#FF9900", "#109618", "#990099",
  "#0099C6", "#DD4477", "#66AA00", "#B82E2E", "#316395"
];

export default function CityComparisonChart() {
  const [allCities, setAllCities] = useState([]);
  const [selectedCities, setSelectedCities] = useState(["北京"]);
  const [type, setType] = useState("PM2.5");
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/api/cities")
      .then(res => res.json())
      .then(data => setAllCities(data));
  }, []);

  useEffect(() => {
    if (selectedCities.length === 0) return;

    const params = new URLSearchParams();
    selectedCities.forEach((c) => params.append("cities", c));
    params.append("type", type);

    fetch(`http://localhost:5000/api/multi_city_timeseries?${params.toString()}`)
      .then((res) => res.json())
      .then((res) => {
        if (!Array.isArray(res)) {
          console.error("返回数据不是数组", res);
          setChartData(null);
          return;
        }

        const uniqueDates = [...new Set(res.map((row) => row.date))].sort();
        const datasets = selectedCities.map((city, index) => {
          const cityData = res.filter((row) => row.city === city);
          const values = uniqueDates.map((d) => {
            const item = cityData.find((r) => r.date === d);
            return item ? item.value : null;
          });
          return {
            label: city,
            data: values,
            borderColor: COLORS[index % COLORS.length],
            backgroundColor: COLORS[index % COLORS.length],
            borderWidth: 2,
          };
        });

        setChartData({ labels: uniqueDates, datasets });
      });
  }, [selectedCities, type]);

  const handleCityChange = (selectedOptions) => {
    const values = selectedOptions.map((opt) => opt.value);
    setSelectedCities(values);
  };

  const cityOptions = allCities.map((c) => ({
    label: c,
    value: c,
    isDisabled: !selectedCities.includes(c) && selectedCities.length >= 10
  }));

  const pollutantOptions = ["AQI", "PM2.5", "PM10", "SO2", "NO2", "O3", "CO"].map((t) => ({
    label: t,
    value: t
  }));

  return (
    <div className="p-4 max-w-screen-xl mx-auto text-white">
      <h1 className="text-3xl font-bold text-center mb-6">中国城市空气质量可视化仪表盘</h1>

      <div className="grid grid-cols-3 grid-rows-2 gap-6">
        {/* 第一块：折线图部分，压缩大小 */}
        <div className="bg-gray-900 p-3 rounded col-span-1 h-[320px] w-[500px] overflow-hidden">
          <h2 className="text-base font-semibold mb-2">多城市趋势图</h2>

          <div className="flex flex-wrap gap-2 mb-3 items-center">
            <div className="w-[240px]">
              {/* <text className="text-sm text-gray-400">选择城市（最多10个）</text> */}
              <Select
                isMulti
                options={cityOptions}
                value={selectedCities.map((c) => ({ label: c, value: c }))}
                onChange={handleCityChange}
                closeMenuOnSelect={false}
                placeholder="选择城市"
              />
            </div>

            <div className="w-[240px]">
              <Select
                options={pollutantOptions}
                value={{ label: type, value: type }}
                onChange={(selected) => setType(selected.value)}
                placeholder="污染物类型"
                isSearchable={false}
              />
            </div>
          </div>

          <div className="h-[200px]">
            {chartData && chartData.datasets ? (
              <Line data={chartData} options={{ maintainAspectRatio: false }} />
            ) : (
              <p className="text-gray-400 text-sm">加载中...</p>
            )}
          </div>
        </div>

        {/* 占位块 2~6，等待其他图表 */}
        <div className="bg-gray-800 p-4 rounded">图表 2</div>
        <div className="bg-gray-800 p-4 rounded">图表 3</div>
        <div className="bg-gray-800 p-4 rounded">图表 4</div>
        <div className="bg-gray-800 p-4 rounded">图表 5</div>
        <div className="bg-gray-800 p-4 rounded">图表 6</div>
      </div>
    </div>
  );
}
