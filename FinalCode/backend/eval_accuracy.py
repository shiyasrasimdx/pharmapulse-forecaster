import numpy as np
import pandas as pd
from forecaster import MedicineForecaster

def evaluate_monthly_accuracy():
    f = MedicineForecaster()
    f.load_data('../SHAFI HAJI JAN2026TOAUG2026(1).xlsx')
    report = f.generate_full_inventory_report()

    # Calculate Monthly Level Accuracy across top high-volume products
    df = f.clean_df
    top_products = df.groupby('Product')['Qty'].sum().sort_values(ascending=False).head(50).index

    results = []
    for prod in top_products:
        prod_df = df[df['Product'] == prod]
        monthly_series = prod_df.set_index('Date').groupby(pd.Grouper(freq='ME'))['Qty'].sum()
        
        if len(monthly_series) >= 3:
            actual_last_month = monthly_series.iloc[-1]
            prev_mean = monthly_series.iloc[:-1].mean()
            mae = abs(actual_last_month - prev_mean)
            wape = (mae / actual_last_month * 100) if actual_last_month > 0 else 0.0
            acc = max(0.0, 100.0 - wape)
            results.append({
                "product": prod,
                "actual_last_month": actual_last_month,
                "predicted_last_month": prev_mean,
                "mae_monthly": round(mae, 2),
                "wape_pct": round(wape, 1),
                "accuracy": round(acc, 1)
            })

    res_df = pd.DataFrame(results)
    print("=== MONTHLY REORDER ACCURACY METRICS (Top 50 Medicines) ===")
    print(f"Average Monthly Accuracy Score: {res_df['accuracy'].mean():.2f}%")
    print(f"Median Monthly Accuracy Score: {res_df['accuracy'].median():.2f}%")
    print(f"Average Monthly MAE Error: {res_df['mae_monthly'].mean():.2f} units/month")
    print(f"Average Monthly WAPE Error: {res_df['wape_pct'].mean():.2f}%")

    print("\n=== SAMPLE TOP MEDICINES MONTHLY ACCURACY ===")
    print(res_df.head(10).to_string(index=False))

if __name__ == '__main__':
    evaluate_monthly_accuracy()
