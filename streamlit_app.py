import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import sys
import plotly.graph_objects as go
import plotly.express as px

# Add backend folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from forecaster import MedicineForecaster

# Page configuration
st.set_page_config(
    page_title="PharmaPulse - AI Medicine Stock Forecaster",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injected Glassmorphism & Modern CSS Theme (Matching React UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
        background-color: #090D16 !important;
        color: #F8FAFC !important;
    }

    /* Main Container Radial Background */
    .stApp {
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(6, 182, 212, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 85% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.04) 0%, transparent 60%) !important;
        background-attachment: fixed !important;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(18, 26, 43, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(6, 182, 212, 0.4);
    }

    /* Header Gradient Text */
    .gradient-cyan {
        background: linear-gradient(135deg, #38BDF8 0%, #06B6D4 50%, #10B981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    .gradient-purple {
        background: linear-gradient(135deg, #C084FC 0%, #8B5CF6 50%, #6366F1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
        margin-right: 4px;
    }
    .badge-urgent { background: rgba(244, 63, 94, 0.2); color: #FB7185; border: 1px solid rgba(244, 63, 94, 0.4); }
    .badge-warning { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-stable { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-a { background: rgba(139, 92, 246, 0.2); color: #C084FC; border: 1px solid rgba(139, 92, 246, 0.4); }
    .badge-b { background: rgba(6, 182, 212, 0.2); color: #38BDF8; border: 1px solid rgba(6, 182, 212, 0.4); }
    .badge-c { background: rgba(148, 163, 184, 0.2); color: #CBD5E1; border: 1px solid rgba(148, 163, 184, 0.4); }

    /* Hide Streamlit Menu/Footer for Clean Look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        font-weight: 600;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #06B6D4 0%, #0D9488 100%) !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_forecaster_engine():
    forecaster = MedicineForecaster()
    dataset_path = os.path.join(os.path.dirname(__file__), 'SHAFI HAJI JAN2026TOAUG2026(1).xlsx')
    if os.path.exists(dataset_path):
        forecaster.load_data(dataset_path)
    return forecaster

forecaster = load_forecaster_engine()

# Sidebar Setup
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
    <div style="background: linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%); padding: 10px; border-radius: 12px; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4);">
        <span style="font-size: 24px;">💊</span>
    </div>
    <div>
        <h2 style="margin: 0; font-size: 1.3rem; font-weight: 800; background: linear-gradient(135deg, #38BDF8 0%, #10B981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">PharmaPulse</h2>
        <p style="margin: 0; font-size: 0.75rem; color: #94A3B8;">AI Stock Forecaster</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Custom Dataset Upload
uploaded_file = st.sidebar.file_uploader("Upload Custom Dataset (.xlsx, .csv)", type=["xlsx", "xls", "csv"])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            xl = pd.ExcelFile(uploaded_file)
            sheet = 'Sheet2' if 'Sheet2' in xl.sheet_names else xl.sheet_names[0]
            df = xl.parse(sheet)
        forecaster = MedicineForecaster()
        forecaster.load_data(df)
        st.sidebar.success(f"Loaded {len(forecaster.clean_df)} records!")
    except Exception as e:
        st.sidebar.error(f"Upload error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Inventory Parameters")
lead_time = st.sidebar.slider("Supplier Lead Time (Days)", min_value=1, max_value=30, value=7)
service_level = st.sidebar.selectbox("Service Level Target", options=[0.90, 0.95, 0.99], format_func=lambda x: f"{int(x*100)}% Service Availability", index=1)
forecast_days = st.sidebar.selectbox("Forecast Horizon", options=[14, 30, 60, 90], format_func=lambda x: f"{x} Days", index=1)

# Generate Full Report
report = forecaster.generate_full_inventory_report(
    lead_time=lead_time,
    service_level=service_level,
    forecast_days=forecast_days
)
overview = report['overview']
products_data = report['products']

# Header Banner
st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-bottom: 24px;">
    <div>
        <h1 class="gradient-cyan" style="font-size: 2rem; margin: 0;">PharmaPulse Dashboard</h1>
        <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">
            AI-powered pharmaceutical purchasing forecast & stock reorder optimization engine
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Tab Layout
tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Overview", "📈 Medicine Deep-Dive", "🛒 Procurement Planner", "⚡ What-If Simulator"])

# --- TAB 1: EXECUTIVE OVERVIEW ---
with tab1:
    # 4 Key Glass Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 600;">TOTAL MEDICINES</span>
            <h2 style="font-size: 1.8rem; font-weight: 800; margin: 8px 0; color: #F8FAFC;">{overview.get('total_products', 0):,}</h2>
            <span style="font-size: 0.75rem; color: #94A3B8;">Active inventory lines</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="glass-card">
            <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 600;">{forecast_days}-DAY DEMAND</span>
            <h2 style="font-size: 1.8rem; font-weight: 800; margin: 8px 0; color: #34D399;">{overview.get('total_forecast_qty', 0):,.0f} <span style="font-size: 0.9rem; color: #94A3B8;">units</span></h2>
            <span style="font-size: 0.75rem; color: #94A3B8;">Ensemble forecast</span>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="glass-card">
            <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 600;">EST. BUDGET (INR)</span>
            <h2 style="font-size: 1.8rem; font-weight: 800; margin: 8px 0; color: #C084FC;">₹{overview.get('total_forecast_cost', 0):,.2f}</h2>
            <span style="font-size: 0.75rem; color: #94A3B8;">Includes safety stock</span>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="glass-card">
            <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 600;">REORDER ALERTS</span>
            <h2 style="font-size: 1.8rem; font-weight: 800; margin: 8px 0; color: #FB7185;">{overview.get('reorder_count', 0)}</h2>
            <span class="badge badge-urgent">{overview.get('high_risk_count', 0)} High Risk</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Full Width Plotly Top Demand Chart
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 4px;">Top Highest Demand Medicines</h3>
        <p style="font-size: 0.8rem; color: #94A3B8; margin-bottom: 16px;">Forecasted unit requirement for next 30 days</p>
    </div>
    """, unsafe_allow_html=True)
    
    if products_data:
        df_p = pd.DataFrame(products_data).sort_values('forecast_qty', ascending=False).head(10)
        
        fig = px.bar(
            df_p,
            x='forecast_qty',
            y='product',
            orientation='h',
            color='forecast_qty',
            color_continuous_scale=['#06B6D4', '#8B5CF6'],
            text='forecast_qty'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94A3B8', family='Plus Jakarta Sans'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Forecast Units'),
            yaxis=dict(autorange='reversed', title=''),
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10),
            height=380
        )
        st.plotly_chart(fig, width="stretch")

# --- TAB 2: MEDICINE DEEP-DIVE ---
with tab2:
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 1.1rem; font-weight: 700;">Single Medicine Time-Series Forecast Visualizer</h3>
        <p style="font-size: 0.8rem; color: #94A3B8;">Deep-dive forecast analysis, confidence bounds, & accuracy backtest metrics</p>
    </div>
    """, unsafe_allow_html=True)

    if products_data:
        prod_list = [p['product'] for p in products_data]
        selected_medicine = st.selectbox("Select Medicine to Analyze:", prod_list)

        fc = forecaster.forecast_product(selected_medicine, forecast_days=forecast_days, lead_time=lead_time, service_level=service_level)
        
        if fc:
            # Header Cards
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"""<div class="glass-card"><span style="font-size:0.75rem; color:#94A3B8;">{forecast_days}-DAY FORECAST</span><h3 style="margin:4px 0; font-weight:800; color:#38BDF8;">{fc['forecast_qty']} units</h3></div>""", unsafe_allow_html=True)
            c2.markdown(f"""<div class="glass-card"><span style="font-size:0.75rem; color:#94A3B8;">SAFETY STOCK (SS)</span><h3 style="margin:4px 0; font-weight:800; color:#FBBF24;">{fc['inventory']['safety_stock']} units</h3></div>""", unsafe_allow_html=True)
            c3.markdown(f"""<div class="glass-card"><span style="font-size:0.75rem; color:#94A3B8;">REORDER POINT (ROP)</span><h3 style="margin:4px 0; font-weight:800; color:#FB7185;">{fc['inventory']['reorder_point']} units</h3></div>""", unsafe_allow_html=True)
            c4.markdown(f"""<div class="glass-card"><span style="font-size:0.75rem; color:#94A3B8;">ESTIMATED COST</span><h3 style="margin:4px 0; font-weight:800; color:#C084FC;">₹{fc['inventory']['forecast_cost']:,.2f}</h3></div>""", unsafe_allow_html=True)

            # Plotly Time-Series Chart with Shaded Band
            chart_df_hist = pd.DataFrame(fc['history_monthly'])
            chart_df_fut = pd.DataFrame(fc['future_monthly'])

            fig_ts = go.Figure()

            # Historical Monthly Actuals Line
            if not chart_df_hist.empty:
                fig_ts.add_trace(go.Scatter(
                    x=chart_df_hist['date'],
                    y=chart_df_hist['qty'],
                    mode='lines+markers',
                    name='Historical Actuals (Units)',
                    line=dict(color='#06B6D4', width=3),
                    marker=dict(size=6)
                ))

            # Future Forecast Line & Confidence Band
            if not chart_df_fut.empty:
                # Add Upper Bound Trace
                fig_ts.add_trace(go.Scatter(
                    x=chart_df_fut['date'],
                    y=chart_df_fut['upper_bound'],
                    mode='lines',
                    name='Upper Confidence Bound',
                    line=dict(color='rgba(139, 92, 246, 0.2)', width=0),
                    showlegend=False
                ))

                # Add Lower Bound Trace (Filled area)
                fig_ts.add_trace(go.Scatter(
                    x=chart_df_fut['date'],
                    y=chart_df_fut['lower_bound'],
                    mode='lines',
                    name='Confidence Bounds',
                    fill='tonexty',
                    fillcolor='rgba(139, 92, 246, 0.15)',
                    line=dict(color='rgba(139, 92, 246, 0.2)', width=0),
                ))

                # Forecast Line
                fig_ts.add_trace(go.Scatter(
                    x=chart_df_fut['date'],
                    y=chart_df_fut['qty'],
                    mode='lines+markers',
                    name='Future Forecast (Units)',
                    line=dict(color='#8B5CF6', width=3, dash='dash'),
                    marker=dict(size=7)
                ))

            fig_ts.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15, 23, 42, 0.5)',
                font=dict(color='#94A3B8', family='Plus Jakarta Sans'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Month'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Demand Units'),
                margin=dict(l=20, r=20, t=20, b=20),
                height=380,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )

            st.plotly_chart(fig_ts, use_container_width=True)

            # Multi-Model Forecast Breakdown Card
            st.markdown("""
            <div class="glass-card">
                <h4 style="font-weight:700; color:#38BDF8; margin-bottom:12px;">🤖 Multi-Model Forecast Breakdown</h4>
                <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05);"><span>Ensemble Blend (Final)</span><strong style="color:#34D399;">{} units/day</strong></div>
                <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05);"><span>Holt-Winters / EWMA</span><strong>{} units/day</strong></div>
                <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05);"><span>Simple Moving Avg (SMA)</span><strong>{} units/day</strong></div>
                <div style="display:flex; justify-content:space-between; padding:8px 0;"><span>Linear Trend Trajectory</span><strong>{} units/day</strong></div>
            </div>
            """.format(
                fc['models']['ensemble_daily'],
                fc['models']['ewma_daily'],
                fc['models']['sma_daily'],
                fc['models']['trend_daily']
            ), unsafe_allow_html=True)

# --- TAB 3: PROCUREMENT PLANNER ---
with tab3:
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 1.1rem; font-weight: 700;">Stock Procurement Planner & Excel Export</h3>
        <p style="font-size: 0.8rem; color: #94A3B8;">Filterable reorder planner with calculated Reorder Points (ROP) and Order Quantities (ROQ)</p>
    </div>
    """, unsafe_allow_html=True)

    if products_data:
        df_proc = pd.DataFrame(products_data)

        # Filter Bar
        f1, f2, f3 = st.columns(3)
        search = f1.text_input("🔍 Search Medicine:")
        abc_f = f2.selectbox("Filter ABC Class:", ["All", "A", "B", "C"])
        status_f = f3.selectbox("Filter Stock Action:", ["All", "URGENT", "REORDER", "STABLE"])

        filtered = df_proc.copy()
        if search:
            filtered = filtered[filtered['product'].str.contains(search, case=False, na=False)]
        if abc_f != "All":
            filtered = filtered[filtered['abc'] == abc_f]
        if status_f != "All":
            filtered = filtered[filtered['stock_status'].str.contains(status_f, na=False)]

        # Display Dataframe
        st.dataframe(
            filtered[['product', 'abc_xyz', 'unit_price', 'avg_daily_demand', 'forecast_qty', 'safety_stock', 'reorder_point', 'recommended_roq', 'forecast_cost', 'stock_status']],
            column_config={
                "product": "Medicine Name",
                "abc_xyz": "Category",
                "unit_price": st.column_config.NumberColumn("Unit Price (₹)", format="₹%.2f"),
                "avg_daily_demand": "Daily Usage",
                "forecast_qty": f"{forecast_days}d Forecast",
                "safety_stock": "Safety Stock (SS)",
                "reorder_point": "Reorder Point (ROP)",
                "recommended_roq": "Order Qty (ROQ)",
                "forecast_cost": st.column_config.NumberColumn("Est. Cost (₹)", format="₹%.2f"),
                "stock_status": "Stock Action"
            },
            width="stretch",
            height=450
        )

        # Excel Download Button
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered.to_excel(writer, index=False, sheet_name='Purchase_Plan')

        st.download_button(
            label="📥 Export Purchase Order Sheet (Excel .xlsx)",
            data=buffer.getvalue(),
            file_name=f"Medicine_Purchase_Plan_{forecast_days}d.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- TAB 4: WHAT-IF SIMULATOR ---
with tab4:
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 1.1rem; font-weight: 700;">⚡ "What-If" Supply Chain Stress Simulator</h3>
        <p style="font-size: 0.8rem; color: #94A3B8;">Test how unexpected supplier delays and epidemic demand surges impact budget and unit requirements</p>
    </div>
    """, unsafe_allow_html=True)

    sim_surge = st.slider("Simulate Demand Surge (%):", min_value=0, max_value=100, value=25)
    sim_lt = st.slider("Simulate Supplier Lead Time (Days):", min_value=1, max_value=30, value=lead_time)

    baseline_cost = overview.get('total_forecast_cost', 0)
    multiplier = 1.0 + (sim_surge / 100.0)
    sim_cost = baseline_cost * multiplier
    cost_diff = sim_cost - baseline_cost

    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(f"""
        <div class="glass-card" style="border:1px solid rgba(139, 92, 246, 0.4); background:rgba(139, 92, 246, 0.12);">
            <span style="font-size:0.8rem; color:#94A3B8;">SIMULATED PROCUREMENT BUDGET</span>
            <h2 style="font-size:2rem; font-weight:800; color:#C084FC; margin:6px 0;">₹{sim_cost:,.2f}</h2>
            <span class="badge badge-urgent">+₹{cost_diff:,.2f} (+{sim_surge}%)</span>
        </div>
        """, unsafe_allow_html=True)

    with sc2:
        st.markdown(f"""
        <div class="glass-card">
            <span style="font-size:0.8rem; color:#94A3B8;">SIMULATED STOCK UNITS NEEDED</span>
            <h2 style="font-size:2rem; font-weight:800; color:#38BDF8; margin:6px 0;">{overview.get('total_forecast_qty', 0) * multiplier:,.0f} units</h2>
            <span style="font-size:0.8rem; color:#94A3B8;">Baseline: {overview.get('total_forecast_qty', 0):,.0f} units</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card">
        <h4 style="color:#FBBF24; margin-bottom:8px;">💡 AI Supply Chain Recommendation:</h4>
        <p style="margin:0; font-size:0.85rem; color:#F8FAFC;">
            Under a <strong>+{sim_surge}% demand surge</strong> and <strong>{sim_lt}-day supplier lead time</strong>, 
            safety stock cushions expand to protect Class A critical medicines. 
            Allocate an additional <strong>₹{cost_diff:,.2f}</strong> in purchasing capital to ensure 0 stockouts.
        </p>
    </div>
    """, unsafe_allow_html=True)
