import React from 'react';
import { Package, TrendingUp, DollarSign, AlertTriangle, Layers, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

export default function OverviewDashboard({ overview, products, setActiveTab, setSelectedProduct }) {
  if (!overview || !products) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading dashboard telemetry...</div>;
  }

  // Top 10 products by 30-day forecast demand
  const topDemandProducts = [...products]
    .sort((a, b) => b.forecast_qty - a.forecast_qty)
    .slice(0, 8)
    .map(p => ({
      name: p.product.length > 20 ? p.product.substring(0, 18) + '...' : p.product,
      fullName: p.product,
      qty: p.forecast_qty,
      cost: p.forecast_cost,
      abc: p.abc
    }));

  // Build 3x3 ABC-XYZ Matrix counts
  const abcTypes = ['A', 'B', 'C'];
  const xyzTypes = ['X', 'Y', 'Z'];
  const matrixCounts = {};
  
  abcTypes.forEach(a => {
    xyzTypes.forEach(x => {
      matrixCounts[`${a}${x}`] = products.filter(p => p.abc === a && p.xyz === x).length;
    });
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Metric Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        
        {/* Card 1: Total Medicines */}
        <div className="glass-panel glass-card-interactive" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Total Medicines</span>
            <div style={{ background: 'rgba(6, 182, 212, 0.15)', padding: '8px', borderRadius: '10px' }}>
              <Package size={20} color="#06B6D4" />
            </div>
          </div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800 }}>{overview.total_products?.toLocaleString()}</h2>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Active inventory lines tracked
          </p>
        </div>

        {/* Card 2: Projected Demand */}
        <div className="glass-panel glass-card-interactive" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>{overview.forecast_days}-Day Projected Demand</span>
            <div style={{ background: 'rgba(16, 185, 129, 0.15)', padding: '8px', borderRadius: '10px' }}>
              <TrendingUp size={20} color="#10B981" />
            </div>
          </div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#34D399' }}>
            {overview.total_forecast_qty?.toLocaleString()} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>units</span>
          </h2>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Multi-model ensemble forecast
          </p>
        </div>

        {/* Card 3: Estimated Order Budget */}
        <div className="glass-panel glass-card-interactive" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Est. Procurement Budget</span>
            <div style={{ background: 'rgba(139, 92, 246, 0.15)', padding: '8px', borderRadius: '10px' }}>
              <DollarSign size={20} color="#8B5CF6" />
            </div>
          </div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#C084FC' }}>
            ₹{overview.total_forecast_cost?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </h2>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Includes safety stock buffer
          </p>
        </div>

        {/* Card 4: Urgent Reorders */}
        <div className="glass-panel glass-card-interactive" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Reorder Alerts</span>
            <div style={{ background: 'rgba(244, 63, 94, 0.15)', padding: '8px', borderRadius: '10px' }}>
              <AlertTriangle size={20} color="#F43F5E" />
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#FB7185' }}>{overview.reorder_count}</h2>
            <span className="badge badge-urgent">{overview.high_risk_count} High Risk</span>
          </div>
          <button
            onClick={() => setActiveTab('procurement')}
            style={{ background: 'none', border: 'none', color: '#38BDF8', fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer', marginTop: '6px', padding: 0 }}
          >
            View reorder list →
          </button>
        </div>

      </div>

      {/* Full Width Top Demand Medicines Chart */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Top Highest Demand Medicines</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Forecasted unit requirement for next {overview.forecast_days} days</p>
          </div>
        </div>

        <div style={{ width: '100%', height: '360px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topDemandProducts} margin={{ top: 10, right: 10, left: 10, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis
                dataKey="name"
                stroke="#94A3B8"
                fontSize={11}
                interval={0}
                angle={-25}
                textAnchor="end"
              />
              <YAxis stroke="#94A3B8" fontSize={11} />
              <Tooltip
                contentStyle={{ background: '#0F172A', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '10px', color: '#F8FAFC' }}
                formatter={(val, name, item) => [`${val} units (₹${item.payload.cost.toLocaleString()})`, 'Forecast Qty']}
                labelFormatter={(label, items) => items[0]?.payload?.fullName || label}
              />
              <Bar dataKey="qty" radius={[6, 6, 0, 0]}>
                {topDemandProducts.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#06B6D4' : '#8B5CF6'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      </div>

    </div>
  );
}
