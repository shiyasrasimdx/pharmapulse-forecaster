import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import sys

# Add backend folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from forecaster import MedicineForecaster

st.set_page_config(
    page_title="PharmaPulse - AI Medicine Stock Forecaster",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #090D16; }
    .stApp { background-color: #090D16; color: #F8FAFC; }
    .metric-card {
        background: rgba(18, 26, 43, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_default_forecaster():
    forecaster = MedicineForecaster()
    dataset_path = os.path.join(os.path.dirname(__file__), 'SHAFI HAJI JAN2026TOAUG2026(1).xlsx')
    if os.path.exists(dataset_path):
        forecaster.load_data(dataset_path)
    return forecaster

forecaster = get_default_forecaster()

# Sidebar Controls
st.sidebar.image("https://img.icons8.com/color/96/000000/pill.png", width=60)
st.sidebar.title("PharmaPulse Engine")
st.sidebar.subheader("Inventory & Forecast Controls")

# Custom File Uploader
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
        st.sidebar.success(f"Loaded custom file: {uploaded_file.name}")
    except Exception as e:
        st.sidebar.error(f"Error parsing file: {e}")

lead_time = st.sidebar.slider("Supplier Lead Time (Days)", min_value=1, max_value=30, value=7)
service_level = st.sidebar.selectbox("Service Level Target", options=[0.90, 0.95, 0.99], format_func=lambda x: f"{int(x*100)}% Availability", index=1)
forecast_days = st.sidebar.selectbox("Forecast Planning Horizon", options=[14, 30, 60, 90], format_func=lambda x: f"{x} Days", index=1)

# Generate Report
report = forecaster.generate_full_inventory_report(
    lead_time=lead_time,
    service_level=service_level,
    forecast_days=forecast_days
)
overview = report['overview']
products_data = report['products']

# Navigation Tabs
st.title("💊 PharmaPulse — Medicine Stock & Demand Forecasting")
st.markdown("AI-driven inventory optimization, time-series forecasting, and automated reorder recommendations.")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Overview", "📈 Medicine Deep-Dive", "🛒 Procurement Planner", "⚡ What-If Simulator"])

# --- TAB 1: EXECUTIVE OVERVIEW ---
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Medicines", f"{overview.get('total_products', 0):,}")
    with col2:
        st.metric(f"{forecast_days}-Day Forecast Demand", f"{overview.get('total_forecast_qty', 0):,.0f} units")
    with col3:
        st.metric("Est. Procurement Budget", f"₹{overview.get('total_forecast_cost', 0):,.2f}")
    with col4:
        st.metric("Reorder Alerts", f"{overview.get('reorder_count', 0)}", delta=f"{overview.get('high_risk_count', 0)} High Risk", delta_color="inverse")

    st.divider()

    col_chart, col_matrix = st.columns([3, 2])
    with col_chart:
        st.subheader("Top Highest Demand Medicines")
        if products_data:
            df_p = pd.DataFrame(products_data).sort_values('forecast_qty', ascending=False).head(10)
            st.bar_chart(df_p.set_index('product')['forecast_qty'])

    with col_matrix:
        st.subheader("ABC / XYZ Pareto Matrix")
        st.caption("ABC = Revenue Pareto | XYZ = Demand Variability")
        abc_xyz_df = forecaster.get_abc_xyz_analysis()
        if not abc_xyz_df.empty:
            matrix_summary = abc_xyz_df.groupby(['ABC', 'XYZ']).size().unstack(fill_value=0)
            st.dataframe(matrix_summary, width="stretch")

# --- TAB 2: MEDICINE DEEP-DIVE ---
with tab2:
    st.subheader("Single Medicine Time-Series Forecast Visualizer")
    if products_data:
        prod_names = [p['product'] for p in products_data]
        selected_prod = st.selectbox("Select Medicine to Analyze:", prod_names)

        fc = forecaster.forecast_product(selected_prod, forecast_days=forecast_days, lead_time=lead_time, service_level=service_level)
        if fc:
            c1, c2, c3 = st.columns(3)
            c1.metric(f"{forecast_days}-Day Forecast", f"{fc['forecast_qty']} units")
            c2.metric("Safety Stock (SS)", f"{fc['inventory']['safety_stock']} units")
            c3.metric("Est. Order Cost", f"₹{fc['inventory']['forecast_cost']:,.2f}")

            # Chart Data
            hist_df = pd.DataFrame(fc['history_monthly'])
            fut_df = pd.DataFrame(fc['future_monthly'])

            st.markdown("#### Monthly Usage vs Projected Demand")
            if not hist_df.empty and not fut_df.empty:
                hist_df['Type'] = 'Historical'
                fut_df['Type'] = 'Forecast'
                combined = pd.concat([hist_df.rename(columns={'qty': 'Units'}), fut_df.rename(columns={'qty': 'Units'})])
                st.line_chart(combined.set_index('date')['Units'])

            st.markdown("#### Model Accuracy & Predictions")
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Ensemble Daily Demand", f"{fc['models']['ensemble_daily']} units/day")
            mc2.metric("Holt-Winters (EWMA)", f"{fc['models']['ewma_daily']} units/day")
            mc3.metric("Moving Avg (SMA)", f"{fc['models']['sma_daily']} units/day")
            mc4.metric("Accuracy Score", f"{fc['metrics']['accuracy_score']}%")

# --- TAB 3: PROCUREMENT PLANNER ---
with tab3:
    st.subheader("Procurement Reorder Planner & Export")
    if products_data:
        df_proc = pd.DataFrame(products_data)
        
        # Filters
        f1, f2, f3 = st.columns(3)
        search = f1.text_input("Search Medicine Name:")
        abc_f = f2.selectbox("Filter ABC Class:", ["All", "A", "B", "C"])
        status_f = f3.selectbox("Filter Stock Action:", ["All", "URGENT", "REORDER", "STABLE"])

        filtered = df_proc.copy()
        if search:
            filtered = filtered[filtered['product'].str.contains(search, case=False, na=False)]
        if abc_f != "All":
            filtered = filtered[filtered['abc'] == abc_f]
        if status_f != "All":
            filtered = filtered[filtered['stock_status'].str.contains(status_f, na=False)]

        st.dataframe(
            filtered[['product', 'abc_xyz', 'unit_price', 'avg_daily_demand', 'forecast_qty', 'safety_stock', 'reorder_point', 'recommended_roq', 'forecast_cost', 'stock_status']],
            width="stretch"
        )

        # Excel Download Button
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered.to_excel(writer, index=False, sheet_name='Purchase_Plan')
        
        st.download_button(
            label="📥 Download Purchase Order Plan (Excel)",
            data=buffer.getvalue(),
            file_name=f"Medicine_Purchase_Plan_{forecast_days}d.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- TAB 4: WHAT-IF STRESS SIMULATOR ---
with tab4:
    st.subheader("Supply Chain Stress Test Simulator")
    sim_surge = st.slider("Simulate Demand Surge (%):", min_value=0, max_value=100, value=25)
    sim_lt = st.slider("Simulate Supplier Lead Time (Days):", min_value=1, max_value=30, value=lead_time)

    baseline_cost = overview.get('total_forecast_cost', 0)
    multiplier = 1.0 + (sim_surge / 100.0)
    sim_cost = baseline_cost * multiplier
    cost_diff = sim_cost - baseline_cost

    sc1, sc2 = st.columns(2)
    sc1.metric("Simulated Procurement Budget", f"₹{sim_cost:,.2f}", delta=f"+₹{cost_diff:,.2f}")
    sc2.metric("Simulated Total Stock Requirement", f"{overview.get('total_forecast_qty', 0) * multiplier:,.0f} units")

    st.info(f"Under a +{sim_surge}% surge and {sim_lt}-day lead time delay, safety stock buffers expand to protect Class A critical medicines. Capital requirement increases by ₹{cost_diff:,.2f}.")
