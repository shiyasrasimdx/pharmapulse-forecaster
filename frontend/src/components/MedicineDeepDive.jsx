import React, { useState, useEffect } from 'react';
import { Search, LineChart, Shield, Calculator, CheckCircle, AlertOctagon, Info } from 'lucide-react';
import { ComposedChart, Line, Area, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';
import axios from 'axios';

export default function MedicineDeepDive({ products, leadTime, serviceLevel, forecastDays }) {
  const [selectedMedicineName, setSelectedMedicineName] = useState(products[0]?.product || '');
  const [productDetail, setProductDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (products && products.length > 0 && !selectedMedicineName) {
      setSelectedMedicineName(products[0].product);
    }
  }, [products]);

  useEffect(() => {
    if (!selectedMedicineName) return;

    setLoading(true);
    axios.get(`http://localhost:5000/api/product/${encodeURIComponent(selectedMedicineName)}`, {
      params: { lead_time: leadTime, service_level: serviceLevel, forecast_days: forecastDays }
    })
    .then(res => {
      setProductDetail(res.data);
      setLoading(false);
    })
    .catch(err => {
      console.error('Failed to fetch medicine detail:', err);
      setLoading(false);
    });
  }, [selectedMedicineName, leadTime, serviceLevel, forecastDays]);

  const filteredProducts = products.filter(p => p.product.toLowerCase().includes(searchTerm.toLowerCase())).slice(0, 30);

  // Build combined history + future forecast dataset for chart
  const chartData = [];
  if (productDetail) {
    if (productDetail.history_monthly) {
      productDetail.history_monthly.forEach(h => {
        chartData.push({
          date: h.date,
          historical: h.qty,
          forecast: null,
          upper: null,
          lower: null
        });
      });
    }

    if (productDetail.future_monthly) {
      // Connect last historical point to first forecast point
      if (chartData.length > 0) {
        const lastHist = chartData[chartData.length - 1];
        lastHist.forecast = lastHist.historical;
      }

      productDetail.future_monthly.forEach(f => {
        chartData.push({
          date: f.date + ' (F)',
          historical: null,
          forecast: f.qty,
          upper: f.upper_bound,
          lower: f.lower_bound
        });
      });
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Selector Bar */}
      <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, minWidth: '300px' }}>
          <Search size={20} color="var(--text-muted)" />
          <input
            type="text"
            className="input-glass"
            style={{ width: '100%' }}
            placeholder="Search medicine by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Select Medicine:</span>
          <select
            className="select-glass"
            style={{ minWidth: '280px' }}
            value={selectedMedicineName}
            onChange={(e) => setSelectedMedicineName(e.target.value)}
          >
            {filteredProducts.map(p => (
              <option key={p.product} value={p.product}>
                [{p.abc_xyz}] {p.product}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="glass-panel" style={{ padding: '60px', textAlign: 'center' }}>
          Running multi-model time series forecasting algorithms...
        </div>
      ) : productDetail ? (
        <>
          {/* Header Summary Panel */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>{productDetail.product}</h2>
                  <span className={`badge badge-${productDetail.abc?.toLowerCase() || 'c'}`}>
                    Category {productDetail.abc_xyz || 'C-Z'}
                  </span>
                  <span className={`badge ${productDetail.inventory?.stock_risk === 'HIGH' ? 'badge-urgent' : 'badge-stable'}`}>
                    Risk: {productDetail.inventory?.stock_risk}
                  </span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Total Historic Sales: {productDetail.total_historical_qty} units across {productDetail.historical_tx_count} purchase bills | Avg Daily Usage: {productDetail.avg_daily_demand} units/day
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{forecastDays}-Day Forecast</span>
                  <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#38BDF8' }}>{productDetail.forecast_qty} units</h3>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Estimated Order Cost</span>
                  <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#C084FC' }}>
                    ₹{productDetail.inventory?.forecast_cost?.toLocaleString()}
                  </h3>
                </div>
              </div>
            </div>
          </div>

          {/* Time Series Forecast Chart */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '4px' }}>
              Historical Usage vs Future Forecast Trend
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
              Continuous monthly series with confidence interval bounds
            </p>

            <div style={{ width: '100%', height: '360px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" stroke="#94A3B8" fontSize={11} />
                  <YAxis stroke="#94A3B8" fontSize={11} />
                  <Tooltip contentStyle={{ background: '#0F172A', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '10px', color: '#F8FAFC' }} />
                  <Legend wrapperStyle={{ paddingTop: '10px' }} />

                  {/* Confidence Interval Band */}
                  <Area type="monotone" dataKey="upper" fill="rgba(139, 92, 246, 0.15)" stroke="none" name="Upper/Lower Bound" />
                  
                  {/* Historical Monthly Actuals */}
                  <Line type="monotone" dataKey="historical" stroke="#06B6D4" strokeWidth={3} dot={{ r: 4 }} name="Historical Actuals (Units)" />
                  
                  {/* Projected Forecast Line */}
                  <Line type="monotone" dataKey="forecast" stroke="#8B5CF6" strokeWidth={3} strokeDasharray="6 6" dot={{ r: 5 }} name="Future Forecast (Units)" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Models Breakdown, Accuracy & Inventory Parameters Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            
            {/* Multi-Model Algorithms Card */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Calculator size={18} color="#06B6D4" /> Multi-Model Daily Forecast Outputs
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(6, 182, 212, 0.1)', borderRadius: '10px', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
                  <span style={{ fontWeight: 700, color: '#38BDF8' }}>Ensemble Blend (Final)</span>
                  <span style={{ fontWeight: 800 }}>{productDetail.models?.ensemble_daily} units/day</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '10px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Holt-Winters / EWMA</span>
                  <span style={{ fontWeight: 600 }}>{productDetail.models?.ewma_daily} units/day</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '10px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Simple Moving Average (SMA)</span>
                  <span style={{ fontWeight: 600 }}>{productDetail.models?.sma_daily} units/day</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '10px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Linear Trend Trajectory</span>
                  <span style={{ fontWeight: 600 }}>{productDetail.models?.trend_daily} units/day</span>
                </div>
              </div>
            </div>

            {/* Model Accuracy Metrics Card */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={18} color="#10B981" /> Backtest Accuracy Metrics
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Accuracy Score</span>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#34D399' }}>{productDetail.metrics?.accuracy_score}%</h4>
                </div>

                <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>WAPE Error</span>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38BDF8' }}>{productDetail.metrics?.wape_pct}%</h4>
                </div>

                <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>MAE Error</span>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{productDetail.metrics?.mae}</h4>
                </div>

                <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>RMSE Error</span>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{productDetail.metrics?.rmse}</h4>
                </div>
              </div>
            </div>

            {/* Inventory Stock Optimization Parameters */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Shield size={18} color="#8B5CF6" /> Inventory Control Parameters
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Safety Stock (SS)</span>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FBBF24' }}>{productDetail.inventory?.safety_stock} units</h4>
                </div>

                <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Reorder Point (ROP)</span>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FB7185' }}>{productDetail.inventory?.reorder_point} units</h4>
                </div>

                <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Recommended Order (ROQ)</span>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#34D399' }}>{productDetail.inventory?.recommended_roq} units</h4>
                </div>

                <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Stock Turnover</span>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{productDetail.inventory?.turnover_days} days</h4>
                </div>
              </div>
            </div>

          </div>
        </>
      ) : null}

    </div>
  );
}
