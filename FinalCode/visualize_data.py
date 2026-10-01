import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure dark glassmorphism chart styling
plt.style.use('dark_background')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']

# 1. Locate and Load Dataset
dataset_path = 'SHAFI HAJI JAN2026TOAUG2026(1).xlsx'
if not os.path.exists(dataset_path):
    dataset_path = 'dataset/FATHIMA KONDOTTY(1).xlsx'

print(f"Loading dataset from: {dataset_path}")
xls = pd.ExcelFile(dataset_path)

# Read Sheet2 (transaction ledger)
sheet_name = 'Sheet2' if 'Sheet2' in xls.sheet_names else xls.sheet_names[0]
df_raw = pd.read_excel(dataset_path, sheet_name=sheet_name, skiprows=2)

# Set headers from the true header row
df_raw.columns = [str(c).strip() for c in df_raw.iloc[0].values]
df = df_raw.iloc[1:].copy()

# 2. Automated Cleaning & Feature Engineering Pipeline
# Filter out summary rows and missing data
df = df[~df['Product'].astype(str).str.lower().str.contains('total|company|area|party|code', na=False)]
df = df.dropna(subset=['Product', 'Date', 'Qty'])

# Type casting
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
df['Value'] = pd.to_numeric(df['Value'], errors='coerce') if 'Value' in df.columns else 0.0

df = df.dropna(subset=['Date', 'Qty'])
df = df[df['Qty'] > 0]  # Retain positive purchase transactions

# Engineer multi-variable features for correlation analysis
df['Month'] = df['Date'].dt.month
df['DayOfWeek'] = df['Date'].dt.dayofweek
df['DayOfYear'] = df['Date'].dt.dayofyear
df['Unit_Price'] = df['Value'] / df['Qty']
df['Name_Length'] = df['Product'].astype(str).str.len()

print(f"Successfully processed {len(df)} clean transaction records with engineered features.")

# 3. Generate and Save Visualizations
os.makedirs('outputs', exist_ok=True)

# --- Chart 1: Top 10 Medicines by Distributed Quantity ---
plt.figure(figsize=(11, 6))
top_products = df.groupby('Product')['Qty'].sum().nlargest(10).sort_values(ascending=True)
top_products.plot(kind='barh', color='#06B6D4', edgecolor='#38BDF8', linewidth=1.2)
plt.title('Top 10 Medicines by Total Distributed Volume (Units)', fontsize=14, fontweight='bold', color='white', pad=15)
plt.xlabel('Total Quantity Distributed', fontsize=11, color='#94A3B8')
plt.ylabel('Medicine Name', fontsize=11, color='#94A3B8')
plt.grid(axis='x', linestyle='--', alpha=0.3, color='#94A3B8')
plt.tight_layout()
plt.savefig('outputs/top_medicines_volume.png', dpi=300, facecolor='#090D16')
plt.close()

# --- Chart 2: Macro Monthly Consumption Trend ---
plt.figure(figsize=(12, 6))
df['MonthYear'] = df['Date'].dt.to_period('M').astype(str)
monthly_trend = df.groupby('MonthYear')['Qty'].sum()
monthly_trend.plot(kind='line', marker='o', color='#8B5CF6', linewidth=3, markersize=8)
plt.title('Macro Monthly Pharmaceutical Consumption Trend', fontsize=14, fontweight='bold', color='white', pad=15)
plt.xlabel('Month-Year', fontsize=11, color='#94A3B8')
plt.ylabel('Total Monthly Quantity (Units)', fontsize=11, color='#94A3B8')
plt.grid(True, linestyle='--', alpha=0.3, color='#94A3B8')
plt.tight_layout()
plt.savefig('outputs/monthly_consumption_trend.png', dpi=300, facecolor='#090D16')
plt.close()

# --- Chart 3: Multi-Variable Correlation Matrix Heatmap ---
plt.figure(figsize=(10, 8))
numeric_cols = ['Qty', 'Value', 'Unit_Price', 'Month', 'DayOfWeek', 'DayOfYear', 'Name_Length']
corr_matrix = df[numeric_cols].corr()

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', cbar=True,
            linewidths=0.8, annot_kws={"size": 10, "weight": "bold"}, vmin=-1, vmax=1)
plt.title('Multi-Variable Correlation Matrix Heatmap', fontsize=14, fontweight='bold', color='white', pad=15)
plt.xticks(rotation=45, ha='right', color='#94A3B8')
plt.yticks(color='#94A3B8')
plt.tight_layout()
chart_3_path = 'outputs/multivariable_correlation_heatmap.png'
plt.savefig(chart_3_path, dpi=300, facecolor='#090D16')
plt.close()
print(f"Saved Multi-Variable Correlation Heatmap to: {chart_3_path}")

print("All charts successfully generated in the 'outputs/' folder!")