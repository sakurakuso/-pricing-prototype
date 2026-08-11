import React, { useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function App() {
  const [form, setForm] = useState({
    city: "",
    address: "",
    category: "餐饮",
    current_price: 20,
    unit_cost: 10,
    daily_sales: 50,
    daily_rent: 200,
    daily_labor: 100,
    other_fixed_daily: 0,
    elasticity: ""
  });
  const [resp, setResp] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    const payload = {
      ...form,
      current_price: Number(form.current_price),
      unit_cost: Number(form.unit_cost),
      daily_sales: Number(form.daily_sales),
      daily_rent: Number(form.daily_rent),
      daily_labor: Number(form.daily_labor),
      other_fixed_daily: Number(form.other_fixed_daily),
      elasticity: form.elasticity === "" ? undefined : Number(form.elasticity)
    };
    try {
      const r = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await r.json();
      setResp(data);
    } catch (err) {
      alert("请求失败: " + err);
    } finally {
      setLoading(false);
    }
  }

  const chartData = resp ? {
    labels: resp.scenarios.map(s => s.label),
    datasets: [
      {
        label: "预计日净利（元）",
        data: resp.scenarios.map(s => s.profit),
        borderColor: "#1976d2",
        backgroundColor: "rgba(25,118,210,0.2)",
        tension: 0.3,
      }
    ]
  } : null;

  return (
    <div className="container">
      <h2>商户定价分析原型（MVP）</h2>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>城市</label>
          <input name="city" value={form.city} onChange={handleChange} />
        </div>
        <div className="field">
          <label>地址 / 门店位置</label>
          <input name="address" value={form.address} onChange={handleChange} />
        </div>
        <div className="field">
          <label>商品类别</label>
          <select name="category" value={form.category} onChange={handleChange}>
            <option>生鲜</option>
            <option>快消</option>
            <option>餐饮</option>
            <option>服装/非必需</option>
            <option>其他</option>
          </select>
        </div>

        <div className="field">
          <label>当前售价（元）</label>
          <input name="current_price" type="number" value={form.current_price} onChange={handleChange} />
        </div>
        <div className=="frontend/src/App.jsx">