import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from forecaster import MedicineForecaster

forecaster = MedicineForecaster()

file1 = os.path.join(os.path.dirname(__file__), '..', 'SHAFI HAJI JAN2026TOAUG2026(1).xlsx')
file2 = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'UNITED_AND_FATHIMA_MEDICALS_2026.csv')

clean_df = forecaster.load_data([file1, file2])

print(f"Total Rows Ingested & Aggregated: {len(clean_df)}")
print(f"Unique Products across shops: {clean_df['Product'].nunique()}")
print(f"Shops detected: {clean_df['Shop_ID'].unique()}")

report = forecaster.generate_full_inventory_report()
print("Overview Report:", report['overview'])
print("\nTop 5 Products across all shops by Forecast Quantity:")
sorted_prods = sorted(report['products'], key=lambda x: x['forecast_qty'], reverse=True)[:5]
for p in sorted_prods:
    print(f"- {p['product']}: Forecast Qty = {p['forecast_qty']}, ABC-XYZ = {p['abc_xyz']}, Stock Status = {p['stock_status']}")
