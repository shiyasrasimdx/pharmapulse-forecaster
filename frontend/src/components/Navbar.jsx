import React from 'react';
import { Pill, LayoutDashboard, LineChart, ShoppingCart, Sliders, Upload, ShieldAlert, Sparkles } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, overview, leadTime, setLeadTime, serviceLevel, setServiceLevel, forecastDays, setForecastDays }) {
  return (
    <header className="glass-panel" style={{ borderRadius: 0, borderTop: 0, borderLeft: 0, borderRight: 0, marginBottom: '24px', padding: '16px 32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%)',
            padding: '10px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px rgba(6, 182, 212, 0.4)'
          }}>
            <Pill size={26} color="#FFFFFF" />
          </div>
          <div>
            <h1 className="gradient-text-cyan" style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: '-0.5px' }}>
              PharmaPulse
            </h1>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>
              AI Stock & Demand Forecasting Engine
            </p>
          </div>
        </div>

        {/* Global Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', background: 'rgba(15, 23, 42, 0.6)', padding: '6px 14px', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Lead Time:</span>
            <select
              className="select-glass"
              style={{ padding: '4px 8px', fontSize: '0.8rem' }}
              value={leadTime}
              onChange={(e) => setLeadTime(Number(e.target.value))}
            >
              <option value={3}>3 Days (Express)</option>
              <option value={7}>7 Days (Standard)</option>
              <option value={14}>14 Days (Regional)</option>
              <option value={21}>21 Days (Import)</option>
            </select>
          </div>

          <div style={{ width: '1px', height: '20px', background: 'var(--border-glass)' }} />

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Service Level:</span>
            <select
              className="select-glass"
              style={{ padding: '4px 8px', fontSize: '0.8rem' }}
              value={serviceLevel}
              onChange={(e) => setServiceLevel(Number(e.target.value))}
            >
              <option value={0.90}>90% (Standard)</option>
              <option value={0.95}>95% (High Availability)</option>
              <option value={0.99}>99% (Critical Care)</option>
            </select>
          </div>

          <div style={{ width: '1px', height: '20px', background: 'var(--border-glass)' }} />

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Horizon:</span>
            <select
              className="select-glass"
              style={{ padding: '4px 8px', fontSize: '0.8rem' }}
              value={forecastDays}
              onChange={(e) => setForecastDays(Number(e.target.value))}
            >
              <option value={14}>14 Days</option>
              <option value={30}>30 Days (1 Month)</option>
              <option value={60}>60 Days (2 Months)</option>
              <option value={90}>90 Days (Quarter)</option>
            </select>
          </div>
        </div>

        {/* Tab Navigation Buttons */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            className={activeTab === 'overview' ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setActiveTab('overview')}
          >
            <LayoutDashboard size={16} /> Overview
          </button>
          
          <button
            className={activeTab === 'forecast' ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setActiveTab('forecast')}
          >
            <LineChart size={16} /> Forecasting
          </button>

          <button
            className={activeTab === 'procurement' ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setActiveTab('procurement')}
          >
            <ShoppingCart size={16} /> Procurement
            {overview?.reorder_count > 0 && (
              <span className="badge badge-urgent" style={{ marginLeft: '4px', padding: '2px 6px' }}>
                {overview.reorder_count}
              </span>
            )}
          </button>

          <button
            className={activeTab === 'simulator' ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setActiveTab('simulator')}
          >
            <Sliders size={16} /> Simulator
          </button>

          <button
            className={activeTab === 'upload' ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setActiveTab('upload')}
          >
            <Upload size={16} /> Custom Data
          </button>
        </nav>

      </div>
    </header>
  );
}
