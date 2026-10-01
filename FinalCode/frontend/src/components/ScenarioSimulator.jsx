import React, { useState, useEffect } from 'react';
import { Sliders, RefreshCw, Zap, ShieldAlert, DollarSign, TrendingUp, ArrowRight } from 'lucide-react';
import axios from 'axios';

export default function ScenarioSimulator({ overview }) {
  const [leadTime, setLeadTime] = useState(7);
  const [demandSurge, setDemandSurge] = useState(25); // +25% default surge
  const [serviceLevel, setServiceLevel] = useState(0.95);
  const [horizon, setHorizon] = useState(30);

  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = () => {
    setLoading(true);
    axios.post('http://localhost:5000/api/simulate', {
      lead_time: leadTime,
      demand_surge_pct: demandSurge,
      service_level: serviceLevel,
      forecast_days: horizon
    })
    .then(res => {
      setSimResult(res.data);
      setLoading(false);
    })
    .catch(err => {
      console.error('Simulation error:', err);
      setLoading(false);
    });
  };

  useEffect(() => {
    runSimulation();
  }, [leadTime, demandSurge, serviceLevel, horizon]);

  const baselineCost = overview?.total_forecast_cost || 0;
  const simCost = simResult?.overview?.total_forecast_cost || 0;
  const costDiff = simCost - baselineCost;

  const baselineQty = overview?.total_forecast_qty || 0;
  const simQty = simResult?.overview?.total_forecast_qty || 0;
  const qtyDiff = simQty - baselineQty;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <h2 style={{ fontSize: '1.3rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Zap size={22} color="#8B5CF6" /> "What-If" Supply Chain Stress Simulator
        </h2>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Test how unexpected supplier lead time delays, epidemic demand surges, and service level targets impact safety stock & budget.
        </p>
      </div>

      {/* Simulator Controls & Live Output Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px' }}>
        
        {/* Controls Card */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={18} color="#06B6D4" /> Scenario Sliders
          </h3>

          {/* Slider 1: Demand Surge */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Demand Surge (%):</label>
              <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#38BDF8' }}>+{demandSurge}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={demandSurge}
              onChange={(e) => setDemandSurge(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#06B6D4', cursor: 'pointer' }}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Simulate seasonal outbreak / sudden demand spike</span>
          </div>

          {/* Slider 2: Supplier Lead Time */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Supplier Lead Time:</label>
              <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FBBF24' }}>{leadTime} Days</span>
            </div>
            <input
              type="range"
              min="1"
              max="30"
              step="1"
              value={leadTime}
              onChange={(e) => setLeadTime(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#F59E0B', cursor: 'pointer' }}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Simulate shipping delays or customs backlog</span>
          </div>

          {/* Slider 3: Target Service Level */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Service Level Target:</label>
              <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#C084FC' }}>{(serviceLevel * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.90"
              max="0.99"
              step="0.01"
              value={serviceLevel}
              onChange={(e) => setServiceLevel(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#8B5CF6', cursor: 'pointer' }}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Target non-stockout probability</span>
          </div>

          {/* Slider 4: Planning Horizon */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Planning Horizon:</label>
              <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#34D399' }}>{horizon} Days</span>
            </div>
            <input
              type="range"
              min="14"
              max="90"
              step="7"
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#10B981', cursor: 'pointer' }}
            />
          </div>

        </div>

        {/* Live Impact Results Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Card 1: Additional Budget Requirement */}
          <div className="glass-panel" style={{ padding: '24px', background: 'rgba(139, 92, 246, 0.12)', border: '1px solid rgba(139, 92, 246, 0.4)' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Simulated Procurement Budget</span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginTop: '6px' }}>
              <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#C084FC' }}>
                ₹{simCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </h2>
              {costDiff > 0 && (
                <span className="badge badge-urgent" style={{ fontSize: '0.85rem' }}>
                  +₹{costDiff.toLocaleString(undefined, { maximumFractionDigits: 0 })} (+{((costDiff/baselineCost)*100).toFixed(1)}%)
                </span>
              )}
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px' }}>
              Baseline Budget: ₹{baselineCost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </p>
          </div>

          {/* Card 2: Total Units Required */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Simulated Stock Units Needed</span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginTop: '6px' }}>
              <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#38BDF8' }}>
                {simQty.toLocaleString()} units
              </h2>
              {qtyDiff > 0 && (
                <span className="badge badge-warning" style={{ fontSize: '0.85rem' }}>
                  +{qtyDiff.toLocaleString()} units
                </span>
              )}
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px' }}>
              Baseline Requirement: {baselineQty.toLocaleString()} units
            </p>
          </div>

          {/* Card 3: Key Recommendation Summary */}
          <div className="glass-panel" style={{ padding: '20px' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '10px', color: '#FBBF24' }}>
              AI Supply Chain Recommendation:
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
              Under a <strong>+{demandSurge}% demand surge</strong> and <strong>{leadTime}-day supplier lead time</strong>, 
              safety stock cushions must expand to prevent stockouts on Class A critical medicines. 
              Allocate an additional <strong>₹{costDiff > 0 ? costDiff.toLocaleString(undefined, { maximumFractionDigits: 0 }) : 0}</strong> in purchasing capital.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}
