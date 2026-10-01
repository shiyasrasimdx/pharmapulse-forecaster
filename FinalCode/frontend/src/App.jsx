import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import OverviewDashboard from './components/OverviewDashboard';
import MedicineDeepDive from './components/MedicineDeepDive';
import ProcurementPlanner from './components/ProcurementPlanner';
import ScenarioSimulator from './components/ScenarioSimulator';
import DataUploader from './components/DataUploader';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [leadTime, setLeadTime] = useState(7);
  const [serviceLevel, setServiceLevel] = useState(0.95);
  const [forecastDays, setForecastDays] = useState(30);

  const [overview, setOverview] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTelemetry = () => {
    setLoading(true);
    setError(null);

    Promise.all([
      axios.get(`${API_BASE}/overview`, { params: { lead_time: leadTime, service_level: serviceLevel, forecast_days: forecastDays } }),
      axios.get(`${API_BASE}/products`, { params: { lead_time: leadTime, service_level: serviceLevel, forecast_days: forecastDays } })
    ])
    .then(([overviewRes, productsRes]) => {
      setOverview(overviewRes.data);
      setProducts(productsRes.data.products);
      setLoading(false);
    })
    .catch(err => {
      console.error('API Error:', err);
      setError('Could not connect to PharmaPulse Backend Server (http://localhost:5000). Please verify backend is running.');
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchTelemetry();
  }, [leadTime, serviceLevel, forecastDays]);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        overview={overview}
        leadTime={leadTime}
        setLeadTime={setLeadTime}
        serviceLevel={serviceLevel}
        setServiceLevel={setServiceLevel}
        forecastDays={forecastDays}
        setForecastDays={setForecastDays}
      />

      <main style={{ flex: 1, padding: '0 32px 40px 32px', maxWidth: '1440px', margin: '0 auto', width: '100%' }}>
        {loading && !overview ? (
          <div className="glass-panel" style={{ padding: '60px', textAlign: 'center', margin: '40px auto', maxWidth: '600px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '8px' }}>Initializing Analytics Telemetry</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Loading 849 medicines & running multi-model time series forecasting...
            </p>
          </div>
        ) : error ? (
          <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', margin: '40px auto', maxWidth: '600px', border: '1px solid rgba(244, 63, 94, 0.4)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#FB7185', marginBottom: '8px' }}>Connection Issue</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>{error}</p>
            <button className="btn-primary" onClick={fetchTelemetry}>Retry Connection</button>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <OverviewDashboard
                overview={overview}
                products={products}
                setActiveTab={setActiveTab}
              />
            )}

            {activeTab === 'forecast' && (
              <MedicineDeepDive
                products={products}
                leadTime={leadTime}
                serviceLevel={serviceLevel}
                forecastDays={forecastDays}
              />
            )}

            {activeTab === 'procurement' && (
              <ProcurementPlanner
                products={products}
                leadTime={leadTime}
                serviceLevel={serviceLevel}
                forecastDays={forecastDays}
              />
            )}

            {activeTab === 'simulator' && (
              <ScenarioSimulator
                overview={overview}
              />
            )}

            {activeTab === 'upload' && (
              <DataUploader
                onUploadSuccess={() => fetchTelemetry()}
              />
            )}
          </>
        )}
      </main>

    </div>
  );
}
