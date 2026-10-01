import os
import sys
import io
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd

# Add current folder to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from forecaster import MedicineForecaster

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize global forecaster with default dataset if present
DEFAULT_DATASET = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SHAFI HAJI JAN2026TOAUG2026(1).xlsx')
forecaster_instance = MedicineForecaster()

if os.path.exists(DEFAULT_DATASET):
    print(f"Pre-loading default dataset: {DEFAULT_DATASET}")
    forecaster_instance.load_data(DEFAULT_DATASET)
else:
    print("Warning: Default dataset not found. Awaiting user file upload.")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "has_data": forecaster_instance.clean_df is not None and not forecaster_instance.clean_df.empty,
        "product_count": len(forecaster_instance.clean_df['Product'].unique()) if forecaster_instance.clean_df is not None else 0
    })

@app.route('/api/overview', methods=['GET'])
def get_overview():
    lead_time = int(request.args.get('lead_time', 7))
    service_level = float(request.args.get('service_level', 0.95))
    forecast_days = int(request.args.get('forecast_days', 30))

    report = forecaster_instance.generate_full_inventory_report(
        lead_time=lead_time,
        service_level=service_level,
        forecast_days=forecast_days
    )
    return jsonify(report['overview'])

@app.route('/api/products', methods=['GET'])
def get_products():
    lead_time = int(request.args.get('lead_time', 7))
    service_level = float(request.args.get('service_level', 0.95))
    forecast_days = int(request.args.get('forecast_days', 30))
    search = request.args.get('search', '').lower().strip()
    abc_filter = request.args.get('abc', '').upper().strip()
    xyz_filter = request.args.get('xyz', '').upper().strip()
    status_filter = request.args.get('status', '').upper().strip()

    report = forecaster_instance.generate_full_inventory_report(
        lead_time=lead_time,
        service_level=service_level,
        forecast_days=forecast_days
    )

    products = report['products']

    # Filters
    if search:
        products = [p for p in products if search in p['product'].lower()]
    if abc_filter:
        products = [p for p in products if p['abc'] == abc_filter]
    if xyz_filter:
        products = [p for p in products if p['xyz'] == xyz_filter]
    if status_filter:
        products = [p for p in products if status_filter in p['stock_status']]

    # Sort: Urgent & A-class first
    products.sort(key=lambda x: (0 if 'URGENT' in x['stock_status'] else 1, 0 if x['abc'] == 'A' else 1, -x['total_sales_val']))

    return jsonify({
        "total_count": len(products),
        "products": products
    })

@app.route('/api/product/<path:product_name>', methods=['GET'])
def get_product_detail(product_name):
    lead_time = int(request.args.get('lead_time', 7))
    service_level = float(request.args.get('service_level', 0.95))
    forecast_days = int(request.args.get('forecast_days', 30))

    fc = forecaster_instance.forecast_product(
        product_name=product_name,
        forecast_days=forecast_days,
        lead_time=lead_time,
        service_level=service_level
    )

    if not fc:
        return jsonify({"error": f"Product '{product_name}' not found."}), 404

    # Merge ABC/XYZ info
    abc_df = forecaster_instance.get_abc_xyz_analysis()
    match = abc_df[abc_df['Product'] == product_name]
    if not match.empty:
        m = match.iloc[0]
        fc['abc'] = str(m['ABC'])
        fc['xyz'] = str(m['XYZ'])
        fc['abc_xyz'] = str(m['ABC_XYZ'])

    return jsonify(fc)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded in request."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Selected file is empty."}), 400

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            xl = pd.ExcelFile(file)
            sheet_name = 'Sheet2' if 'Sheet2' in xl.sheet_names else xl.sheet_names[0]
            df = xl.parse(sheet_name)

        forecaster_instance.load_data(df)
        report = forecaster_instance.generate_full_inventory_report()

        return jsonify({
            "message": f"Successfully loaded dataset with {len(forecaster_instance.clean_df)} records.",
            "overview": report['overview']
        })
    except Exception as e:
        return jsonify({"error": f"Failed to parse dataset file: {str(e)}"}), 500

@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    data = request.json or {}
    lead_time = int(data.get('lead_time', 7))
    service_level = float(data.get('service_level', 0.95))
    forecast_days = int(data.get('forecast_days', 30))
    demand_surge_pct = float(data.get('demand_surge_pct', 0.0)) # e.g. +20% -> 20.0

    report = forecaster_instance.generate_full_inventory_report(
        lead_time=lead_time,
        service_level=service_level,
        forecast_days=forecast_days
    )

    # Apply demand surge multiplier if specified
    if demand_surge_pct != 0.0:
        multiplier = 1.0 + (demand_surge_pct / 100.0)
        report['overview']['total_forecast_qty'] = float(round(report['overview']['total_forecast_qty'] * multiplier, 2))
        report['overview']['total_forecast_cost'] = float(round(report['overview']['total_forecast_cost'] * multiplier, 2))
        
        for p in report['products']:
            p['forecast_qty'] = float(round(p['forecast_qty'] * multiplier, 2))
            p['recommended_roq'] = float(round(p['recommended_roq'] * multiplier, 2))
            p['forecast_cost'] = float(round(p['forecast_cost'] * multiplier, 2))

    return jsonify(report)

@app.route('/api/export', methods=['GET'])
def export_purchase_order():
    lead_time = int(request.args.get('lead_time', 7))
    service_level = float(request.args.get('service_level', 0.95))
    forecast_days = int(request.args.get('forecast_days', 30))

    report = forecaster_instance.generate_full_inventory_report(
        lead_time=lead_time,
        service_level=service_level,
        forecast_days=forecast_days
    )

    export_df = pd.DataFrame(report['products'])
    export_df = export_df.rename(columns={
        'product': 'Medicine Name',
        'abc_xyz': 'Category (ABC-XYZ)',
        'historical_qty': 'Historical Sales Qty',
        'unit_price': 'Unit Price (₹)',
        'avg_daily_demand': 'Avg Daily Usage',
        'forecast_qty': f'{forecast_days}-Day Forecast Qty',
        'safety_stock': 'Safety Stock (SS)',
        'reorder_point': 'Reorder Point (ROP)',
        'recommended_roq': 'Reorder Quantity (ROQ)',
        'forecast_cost': 'Total Order Cost (₹)',
        'stock_risk': 'Risk Level',
        'stock_status': 'Stock Action'
    })

    cols_to_keep = [
        'Medicine Name', 'Category (ABC-XYZ)', 'Unit Price (₹)', 'Avg Daily Usage',
        f'{forecast_days}-Day Forecast Qty', 'Safety Stock (SS)', 'Reorder Point (ROP)',
        'Reorder Quantity (ROQ)', 'Total Order Cost (₹)', 'Risk Level', 'Stock Action'
    ]
    export_df = export_df[[c for c in cols_to_keep if c in export_df.columns]]

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Purchase_Order_Plan')
    out.seek(0)

    return send_file(
        out,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'Medicine_Stock_Purchase_Plan_{forecast_days}d.xlsx'
    )

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if path != "" and os.path.exists(os.path.join(static_dir, path)):
        return send_from_directory(static_dir, path)
    elif os.path.exists(os.path.join(static_dir, 'index.html')):
        return send_from_directory(static_dir, 'index.html')
    else:
        return jsonify({"status": "PharmaPulse API server running", "message": "Visit /api/health for system status"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Medicine Stock Forecaster REST API server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
