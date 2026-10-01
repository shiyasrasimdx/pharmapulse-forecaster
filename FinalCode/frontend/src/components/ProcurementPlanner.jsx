import React, { useState } from 'react';
import { Download, Search, Filter, ShoppingCart, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function ProcurementPlanner({ products, leadTime, serviceLevel, forecastDays }) {
  const [search, setSearch] = useState('');
  const [abcFilter, setAbcFilter] = useState('ALL');
  const [xyzFilter, setXyzFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredProducts = products.filter(p => {
    const matchSearch = p.product.toLowerCase().includes(search.toLowerCase());
    const matchAbc = abcFilter === 'ALL' || p.abc === abcFilter;
    const matchXyz = xyzFilter === 'ALL' || p.xyz === xyzFilter;
    const matchStatus = statusFilter === 'ALL' || p.stock_status.includes(statusFilter);
    return matchSearch && matchAbc && matchXyz && matchStatus;
  });

  const handleExportExcel = () => {
    const exportUrl = `http://localhost:5000/api/export?lead_time=${leadTime}&service_level=${serviceLevel}&forecast_days=${forecastDays}`;
    window.open(exportUrl, '_blank');
  };

  const totalFilteredCost = filteredProducts.reduce((acc, p) => acc + (p.forecast_cost || 0), 0);
  const totalFilteredUnits = filteredProducts.reduce((acc, p) => acc + (p.recommended_roq || 0), 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Header Bar */}
      <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShoppingCart size={22} color="#06B6D4" /> Stock Procurement Planner
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Calculated reorder quantities (ROQ) based on Lead Time ({leadTime}d) and Service Level ({serviceLevel * 100}%)
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Filtered Order Total:</span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38BDF8' }}>
              {totalFilteredUnits.toLocaleString()} units (₹{totalFilteredCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
            </h3>
          </div>

          <button className="btn-primary" onClick={handleExportExcel}>
            <Download size={16} /> Export Purchase Order (Excel)
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-panel" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
        
        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: '240px' }}>
          <Search size={18} color="var(--text-muted)" />
          <input
            type="text"
            className="input-glass"
            style={{ width: '100%' }}
            placeholder="Search medicine..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* ABC Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>ABC:</span>
          <select className="select-glass" value={abcFilter} onChange={(e) => setAbcFilter(e.target.value)}>
            <option value="ALL">All ABC</option>
            <option value="A">Class A (Top 80% Rev)</option>
            <option value="B">Class B (15% Rev)</option>
            <option value="C">Class C (5% Rev)</option>
          </select>
        </div>

        {/* XYZ Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>XYZ:</span>
          <select className="select-glass" value={xyzFilter} onChange={(e) => setXyzFilter(e.target.value)}>
            <option value="ALL">All XYZ</option>
            <option value="X">Class X (Predictable)</option>
            <option value="Y">Class Y (Variable)</option>
            <option value="Z">Class Z (Erratic)</option>
          </select>
        </div>

        {/* Status Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Action:</span>
          <select className="select-glass" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="ALL">All Statuses</option>
            <option value="URGENT">Urgent Only</option>
            <option value="REORDER">Reorder Only</option>
            <option value="STABLE">Stable Only</option>
          </select>
        </div>

      </div>

      {/* Reorder Table */}
      <div className="glass-panel" style={{ padding: '0', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ background: 'rgba(15, 23, 42, 0.8)', borderBottom: '1px solid var(--border-glass)', color: 'var(--text-muted)', textAlign: 'left' }}>
              <th style={{ padding: '14px 18px' }}>Medicine Name</th>
              <th style={{ padding: '14px 12px' }}>Category</th>
              <th style={{ padding: '14px 12px' }}>Unit Price (₹)</th>
              <th style={{ padding: '14px 12px' }}>Daily Demand</th>
              <th style={{ padding: '14px 12px' }}>{forecastDays}d Forecast</th>
              <th style={{ padding: '14px 12px' }}>Safety Stock (SS)</th>
              <th style={{ padding: '14px 12px' }}>Reorder Point (ROP)</th>
              <th style={{ padding: '14px 12px' }}>Order Qty (ROQ)</th>
              <th style={{ padding: '14px 12px' }}>Est. Cost (₹)</th>
              <th style={{ padding: '14px 18px', textAlign: 'center' }}>Stock Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredProducts.slice(0, 100).map((p, idx) => (
              <tr
                key={p.product + idx}
                style={{
                  borderBottom: '1px solid rgba(255,255,255,0.03)',
                  transition: 'background 0.15s ease',
                  background: idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(6, 182, 212, 0.05)'}
                onMouseLeave={(e) => e.currentTarget.style.background = idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)'}
              >
                <td style={{ padding: '14px 18px', fontWeight: 600 }}>{p.product}</td>
                <td style={{ padding: '14px 12px' }}>
                  <span className={`badge badge-${p.abc.toLowerCase()}`}>
                    {p.abc_xyz}
                  </span>
                </td>
                <td style={{ padding: '14px 12px' }}>₹{p.unit_price}</td>
                <td style={{ padding: '14px 12px' }}>{p.avg_daily_demand}</td>
                <td style={{ padding: '14px 12px', fontWeight: 600 }}>{p.forecast_qty}</td>
                <td style={{ padding: '14px 12px', color: '#FBBF24' }}>{p.safety_stock}</td>
                <td style={{ padding: '14px 12px', color: '#FB7185' }}>{p.reorder_point}</td>
                <td style={{ padding: '14px 12px', fontWeight: 700, color: '#34D399' }}>{p.recommended_roq}</td>
                <td style={{ padding: '14px 12px', fontWeight: 600 }}>₹{p.forecast_cost?.toLocaleString()}</td>
                <td style={{ padding: '14px 18px', textAlign: 'center' }}>
                  <span className={`badge ${p.stock_status.includes('URGENT') ? 'badge-urgent' : p.stock_status.includes('REORDER') ? 'badge-warning' : 'badge-stable'}`}>
                    {p.stock_status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredProducts.length > 100 && (
          <div style={{ padding: '14px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem', borderTop: '1px solid var(--border-glass)' }}>
            Showing top 100 matching medicines of {filteredProducts.length} total. Export Excel to view full list.
          </div>
        )}
      </div>

    </div>
  );
}
