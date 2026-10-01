import os
from forecaster import MedicineForecaster

def test_forecaster():
    dataset_path = '../SHAFI HAJI JAN2026TOAUG2026(1).xlsx' if os.path.exists('../SHAFI HAJI JAN2026TOAUG2026(1).xlsx') else 'SHAFI HAJI JAN2026TOAUG2026(1).xlsx'
    print(f"Testing dataset: {dataset_path}")
    assert os.path.exists(dataset_path), "Dataset file not found!"

    forecaster = MedicineForecaster()
    clean_df = forecaster.load_data(dataset_path)
    print(f"Cleaned dataset rows: {len(clean_df)}")
    assert len(clean_df) > 0, "Cleaned dataset should not be empty"

    # Test ABC/XYZ Analysis
    abc_xyz = forecaster.get_abc_xyz_analysis()
    print(f"ABC/XYZ products analyzed: {len(abc_xyz)}")
    assert len(abc_xyz) > 0
    print("ABC Counts:", abc_xyz['ABC'].value_counts().to_dict())
    print("XYZ Counts:", abc_xyz['XYZ'].value_counts().to_dict())

    # Test Single Product Forecast
    top_product = abc_xyz.iloc[0]['Product']
    print(f"\nTesting forecast for top product: {top_product}")
    fc = forecaster.forecast_product(top_product, forecast_days=30, lead_time=7, service_level=0.95)
    assert fc is not None
    print(f"Forecast 30-day Qty: {fc['forecast_qty']}")
    print(f"Safety Stock: {fc['inventory']['safety_stock']}")
    print(f"Reorder Point: {fc['inventory']['reorder_point']}")
    print(f"Recommended ROQ: {fc['inventory']['recommended_roq']}")
    print(f"Models: {fc['models']}")

    # Test Full Inventory Report
    print("\nGenerating full inventory report...")
    report = forecaster.generate_full_inventory_report(lead_time=7, service_level=0.95, forecast_days=30)
    print("Overview Summary:", report['overview'])
    assert report['overview']['total_products'] > 0
    print("\nSUCCESS! All unit tests passed cleanly.")

if __name__ == '__main__':
    test_forecaster()
