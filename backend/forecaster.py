import pandas as pd
import numpy as np
import re
import os
from datetime import timedelta
import math

class MedicineForecaster:
    def __init__(self, df=None):
        self.raw_df = None
        self.clean_df = None
        self.product_summaries = {}
        if df is not None:
            self.load_data(df)

    def load_data(self, df_or_filepath):
        """Loads and normalizes dataset from single or multiple Excel/CSV files/DataFrames."""
        if isinstance(df_or_filepath, list):
            cleaned_dfs = []
            for idx, item in enumerate(df_or_filepath):
                shop_label = f"Shop_{idx+1}"
                if hasattr(item, 'name'):
                    shop_label = item.name.split('.')[0]
                elif isinstance(item, str):
                    shop_label = os.path.basename(item).split('.')[0]

                try:
                    if isinstance(item, str):
                        if item.endswith('.csv'):
                            raw = pd.read_csv(item)
                        else:
                            xl = pd.ExcelFile(item)
                            sheet_name = 'Sheet2' if 'Sheet2' in xl.sheet_names else xl.sheet_names[0]
                            raw = xl.parse(sheet_name)
                    elif hasattr(item, 'read'): # Streamlit UploadedFile object
                        if getattr(item, 'name', '').endswith('.csv'):
                            raw = pd.read_csv(item)
                        else:
                            xl = pd.ExcelFile(item)
                            sheet_name = 'Sheet2' if 'Sheet2' in xl.sheet_names else xl.sheet_names[0]
                            raw = xl.parse(sheet_name)
                    elif isinstance(item, pd.DataFrame):
                        raw = item.copy()
                    else:
                        continue
                    
                    c_df = self._clean_and_structure_data(raw)
                    if not c_df.empty:
                        c_df['Shop_ID'] = shop_label
                        cleaned_dfs.append(c_df)
                except Exception as e:
                    print(f"Error parsing file {item}: {e}")

            if cleaned_dfs:
                self.clean_df = pd.concat(cleaned_dfs, ignore_index=True)
            else:
                self.clean_df = pd.DataFrame(columns=['Date', 'Product', 'Qty', 'Value', 'Shop_ID'])
            return self.clean_df

        # Single source processing
        if isinstance(df_or_filepath, str):
            if df_or_filepath.endswith('.csv'):
                df = pd.read_csv(df_or_filepath)
            else:
                xl = pd.ExcelFile(df_or_filepath)
                sheet_name = 'Sheet2' if 'Sheet2' in xl.sheet_names else xl.sheet_names[0]
                df = xl.parse(sheet_name)
        elif hasattr(df_or_filepath, 'read'):
            if getattr(df_or_filepath, 'name', '').endswith('.csv'):
                df = pd.read_csv(df_or_filepath)
            else:
                xl = pd.ExcelFile(df_or_filepath)
                sheet_name = 'Sheet2' if 'Sheet2' in xl.sheet_names else xl.sheet_names[0]
                df = xl.parse(sheet_name)
        else:
            df = df_or_filepath.copy()

        self.raw_df = df
        self.clean_df = self._clean_and_structure_data(df)
        return self.clean_df

    def _clean_and_structure_data(self, df):
        """
        Cleans data and maps standard columns: Date, Product, Qty, Value, BillNo.
        Handles row offsets common in hospital/pharmacy export files.
        """
        # Search for header row if needed
        cols = [str(c).strip().lower() for c in df.columns]
        
        # Check if first few rows contain header text like 'Code', 'Product', 'Qty'
        header_row_idx = None
        for idx in range(min(15, len(df))):
            row_vals = [str(val).lower() for val in df.iloc[idx].values]
            if any('product' in v or 'item' in v for v in row_vals) and any('qty' in v or 'quantity' in v for v in row_vals):
                header_row_idx = idx
                break

        if header_row_idx is not None:
            new_cols = df.iloc[header_row_idx].values
            df = df.iloc[header_row_idx + 1:].copy()
            df.columns = new_cols

        # Prioritize exact column name matching over generic regex
        exact_map = {
            'date': 'Date',
            'product': 'Product',
            'item': 'Product',
            'description': 'Product',
            'qty': 'Qty',
            'quantity': 'Qty',
            'value': 'Value',
            'amount': 'Value',
            'price': 'Value',
            'billno': 'BillNo',
            'bill_no': 'BillNo',
            'invoice': 'BillNo'
        }

        mapped_cols = {}
        # Pass 1: Exact matches
        for c in df.columns:
            c_str = str(c).strip().lower()
            if c_str in exact_map and exact_map[c_str] not in mapped_cols.values():
                mapped_cols[c] = exact_map[c_str]

        # Pass 2: Regex fuzzy matching for remaining unmapped standard columns
        for c in df.columns:
            if c in mapped_cols:
                continue
            c_lower = str(c).strip().lower()
            if 'Date' not in mapped_cols.values() and re.search(r'date|time|dt', c_lower):
                mapped_cols[c] = 'Date'
            elif 'Product' not in mapped_cols.values() and re.search(r'prod|item|desc|medicin', c_lower):
                mapped_cols[c] = 'Product'
            elif 'Qty' not in mapped_cols.values() and re.search(r'qty|quantity|unit', c_lower):
                mapped_cols[c] = 'Qty'
            elif 'Value' not in mapped_cols.values() and re.search(r'val|amount|price|total|rev', c_lower):
                mapped_cols[c] = 'Value'

        cleaned = df.rename(columns=mapped_cols)
        
        # Ensure minimum required columns exist
        if 'Product' not in cleaned.columns or 'Qty' not in cleaned.columns:
            # Fallback column mapping if auto-detect failed
            col_list = list(cleaned.columns)
            if len(col_list) >= 8:
                cleaned = cleaned.iloc[:, [2, 4, 6, 7]].copy()
                cleaned.columns = ['Date', 'Product', 'Qty', 'Value']

        # Ensure unique columns
        cleaned = cleaned.loc[:, ~cleaned.columns.duplicated()].copy()

        # Process types & clean values
        # Extract product as a Series
        prod_series = cleaned['Product']
        if isinstance(prod_series, pd.DataFrame):
            prod_series = prod_series.iloc[:, 0]

        cleaned['Product'] = prod_series.astype(str).str.strip()
        # Exclude invalid product names like NaN, total lines, headers
        invalid_patterns = r'total|company|area:|party|code|page|subtotal|nan'
        cleaned = cleaned[~cleaned['Product'].str.lower().str.contains(invalid_patterns, na=False)]
        cleaned = cleaned[cleaned['Product'].str.len() > 1]

        cleaned['Date'] = pd.to_datetime(cleaned['Date'], errors='coerce')
        cleaned['Qty'] = pd.to_numeric(cleaned['Qty'], errors='coerce').fillna(0)
        
        if 'Value' in cleaned.columns:
            cleaned['Value'] = pd.to_numeric(cleaned['Value'], errors='coerce').fillna(0)
        else:
            cleaned['Value'] = cleaned['Qty'] * 10.0 # Default unit estimate if absent

        cleaned = cleaned.dropna(subset=['Date', 'Product'])
        
        # Exclude returns/adjustments with negative qty for baseline demand, but record net
        cleaned = cleaned[cleaned['Qty'] > 0].sort_values('Date')
        
        return cleaned

    def get_abc_xyz_analysis(self, df=None):
        """
        Calculates ABC Pareto (Revenue) & XYZ (Predictability / Variation) matrix.
        ABC: A (top 80% sales), B (next 15%), C (bottom 5%)
        XYZ: X (CV <= 0.5 - predictable), Y (0.5 < CV <= 1.0), Z (CV > 1.0 - erratic)
        """
        if df is None:
            df = self.clean_df

        if df is None or df.empty:
            return pd.DataFrame()

        # Group by Product
        grp = df.groupby('Product').agg(
            TotalQty=('Qty', 'sum'),
            TotalValue=('Value', 'sum'),
            TxCount=('Qty', 'count'),
            FirstDate=('Date', 'min'),
            LastDate=('Date', 'max')
        ).reset_index()

        # Unit Price
        grp['AvgUnitPrice'] = np.where(grp['TotalQty'] > 0, grp['TotalValue'] / grp['TotalQty'], 0)

        # ABC Analysis
        grp = grp.sort_values(by='TotalValue', ascending=False)
        grp['CumValue'] = grp['TotalValue'].cumsum()
        total_rev = grp['TotalValue'].sum() if grp['TotalValue'].sum() > 0 else 1
        grp['CumPercent'] = grp['CumValue'] / total_rev

        def assign_abc(pct):
            if pct <= 0.80:
                return 'A'
            elif pct <= 0.95:
                return 'B'
            else:
                return 'C'

        grp['ABC'] = grp['CumPercent'].apply(assign_abc)

        # XYZ Analysis (Monthly Coefficient of Variation)
        # Resample by Month for each product
        df_monthly = df.set_index('Date').groupby(['Product', pd.Grouper(freq='ME')])['Qty'].sum().reset_index()
        
        xyz_stats = df_monthly.groupby('Product')['Qty'].agg(
            MeanMonthly=('mean'),
            StdMonthly=('std')
        ).reset_index()

        xyz_stats['CV'] = np.where(
            xyz_stats['MeanMonthly'] > 0,
            xyz_stats['StdMonthly'].fillna(0) / xyz_stats['MeanMonthly'],
            999.0
        )

        def assign_xyz(cv):
            if cv <= 0.5:
                return 'X'
            elif cv <= 1.0:
                return 'Y'
            else:
                return 'Z'

        xyz_stats['XYZ'] = xyz_stats['CV'].apply(assign_xyz)

        # Merge ABC & XYZ
        abc_xyz = pd.merge(grp, xyz_stats[['Product', 'MeanMonthly', 'StdMonthly', 'CV', 'XYZ']], on='Product', how='left')
        abc_xyz['XYZ'] = abc_xyz['XYZ'].fillna('Z')
        abc_xyz['ABC_XYZ'] = abc_xyz['ABC'] + abc_xyz['XYZ']

        return abc_xyz

    def forecast_product(self, product_name, forecast_days=30, lead_time=7, service_level=0.95, df=None):
        """
        Forecasting Engine for a specific product.
        Generates daily/monthly predictions using Exponential Smoothing, Moving Average, and Trend.
        Computes Safety Stock, Reorder Point (ROP), and Order Quantity (ROQ).
        """
        if df is None:
            df = self.clean_df

        prod_df = df[df['Product'] == product_name].copy()
        if prod_df.empty:
            return None

        # Build continuous daily demand series
        min_date = prod_df['Date'].min()
        max_date = prod_df['Date'].max()
        
        # Ensure span covers at least 30 days
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        daily_series = prod_df.groupby('Date')['Qty'].sum().reindex(date_range, fill_value=0.0)

        total_days = len(daily_series)
        total_qty = daily_series.sum()
        avg_daily_demand = daily_series.mean()
        std_daily_demand = daily_series.std() if total_days > 1 else 0.0

        # Monthly aggregation for historical chart
        monthly_series = prod_df.set_index('Date').groupby(pd.Grouper(freq='ME'))['Qty'].sum()
        history_monthly = [
            {"date": d.strftime("%Y-%m"), "qty": float(q)}
            for d, q in monthly_series.items()
        ]

        # Forecast algorithms (Daily level)
        # 1. Simple / Weighted Moving Average (SMA / WMA)
        window = min(30, max(7, total_days))
        recent_daily = daily_series.iloc[-window:]
        sma_daily = recent_daily.mean()

        # 2. Holt-Winters / Exponential Smoothing (EWMA)
        ewma_daily = daily_series.ewm(span=min(14, total_days), adjust=False).mean().iloc[-1]

        # 3. Linear Trend Regression
        x = np.arange(total_days)
        y = daily_series.values
        if total_days >= 5 and np.std(x) > 0:
            slope, intercept = np.polyfit(x, y, 1)
            # Clip slope to prevent extreme explosive trend
            slope = np.clip(slope, -avg_daily_demand * 0.1, avg_daily_demand * 0.1)
            trend_daily = max(0, intercept + slope * (total_days + forecast_days / 2))
        else:
            trend_daily = avg_daily_demand

        # Ensemble forecast (Weighted combination)
        ensemble_daily = (0.4 * ewma_daily) + (0.4 * sma_daily) + (0.2 * trend_daily)
        ensemble_daily = max(0.01, ensemble_daily) # Minimum baseline demand

        forecast_qty = float(round(ensemble_daily * forecast_days, 2))

        # Monthly projected forecast points
        last_month = max_date.replace(day=1)
        future_monthly = []
        months_to_predict = max(1, math.ceil(forecast_days / 30.0))
        for m in range(1, months_to_predict + 1):
            next_m = last_month + pd.DateOffset(months=m)
            m_qty = float(round(ensemble_daily * 30.0, 2))
            future_monthly.append({
                "date": next_m.strftime("%Y-%m"),
                "qty": m_qty,
                "upper_bound": float(round(m_qty * 1.25, 2)),
                "lower_bound": float(round(max(0, m_qty * 0.75), 2))
            })

        # Inventory Optimization Math
        # Service Level Z-Score mapping
        z_scores = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
        z = z_scores.get(service_level, 1.645)

        # Safety Stock = Z * std_daily * sqrt(lead_time)
        safety_stock = float(round(z * std_daily_demand * math.sqrt(lead_time), 2))
        
        # Reorder Point (ROP) = (Avg Daily Demand * Lead Time) + Safety Stock
        reorder_point = float(round((avg_daily_demand * lead_time) + safety_stock, 2))

        # Recommended Reorder Quantity (ROQ) assuming 0 current stock baseline
        recommended_roq = float(round(forecast_qty + safety_stock, 2))

        # Avg Unit Price & Total Forecast Budget
        unit_price = float(round(prod_df['Value'].sum() / total_qty, 2)) if total_qty > 0 else 10.0
        forecast_cost = float(round(recommended_roq * unit_price, 2))

        # Backtesting Accuracy Metrics (Evaluating at monthly aggregated level)
        if len(history_monthly) > 0:
            hist_qtys = [h['qty'] for h in history_monthly]
            monthly_mean = float(np.mean(hist_qtys)) if len(hist_qtys) > 0 else 1.0
            monthly_predicted = float(round(ensemble_daily * 30.0, 2))
            
            mae = float(round(abs(monthly_mean - monthly_predicted), 2))
            rmse = float(round(float(np.sqrt(np.mean((np.array(hist_qtys) - monthly_predicted)**2))), 2)) if len(hist_qtys) > 0 else mae
            wape = float(round((mae / monthly_mean * 100), 1)) if monthly_mean > 0 else 0.0
            acc_score = float(round(max(0.0, 100.0 - wape), 1))
        else:
            mae = 0.0
            rmse = 0.0
            wape = 0.0
            acc_score = 100.0

        # Stockout Risk Rating & FEFO Turnover Rating
        cv = (std_daily_demand / avg_daily_demand) if avg_daily_demand > 0 else 1.0
        if cv > 1.2 and forecast_qty > 20:
            stock_risk = 'HIGH'
        elif cv > 0.6:
            stock_risk = 'MEDIUM'
        else:
            stock_risk = 'LOW'

        turnover_days = float(round(recommended_roq / avg_daily_demand, 1)) if avg_daily_demand > 0 else 999.0

        return {
            "product": product_name,
            "total_historical_qty": float(total_qty),
            "historical_tx_count": int(len(prod_df)),
            "avg_daily_demand": float(round(avg_daily_demand, 2)),
            "std_daily_demand": float(round(std_daily_demand, 2)),
            "forecast_days": forecast_days,
            "forecast_qty": forecast_qty,
            "models": {
                "ensemble_daily": float(round(ensemble_daily, 2)),
                "ewma_daily": float(round(ewma_daily, 2)),
                "sma_daily": float(round(sma_daily, 2)),
                "trend_daily": float(round(trend_daily, 2))
            },
            "metrics": {
                "mae": mae,
                "rmse": rmse,
                "wape_pct": wape,
                "accuracy_score": float(round(max(0, 100.0 - wape), 1))
            },
            "inventory": {
                "lead_time_days": lead_time,
                "service_level": service_level,
                "z_score": z,
                "safety_stock": safety_stock,
                "reorder_point": reorder_point,
                "recommended_roq": recommended_roq,
                "unit_price": unit_price,
                "forecast_cost": forecast_cost,
                "stock_risk": stock_risk,
                "turnover_days": turnover_days
            },
            "history_monthly": history_monthly,
            "future_monthly": future_monthly
        }

    def generate_full_inventory_report(self, lead_time=7, service_level=0.95, forecast_days=30):
        """Generates overview summary & inventory plan for all products."""
        if self.clean_df is None or self.clean_df.empty:
            return {"overview": {}, "products": []}

        abc_xyz_df = self.get_abc_xyz_analysis()
        
        products_report = []
        total_forecast_qty = 0.0
        total_forecast_cost = 0.0
        high_risk_count = 0
        reorder_count = 0

        for _, row in abc_xyz_df.iterrows():
            p_name = row['Product']
            fc = self.forecast_product(
                p_name,
                forecast_days=forecast_days,
                lead_time=lead_time,
                service_level=service_level
            )

            if fc is None:
                continue

            # Stocking Status classification
            roq = fc['inventory']['recommended_roq']
            risk = fc['inventory']['stock_risk']

            if risk == 'HIGH' or row['ABC'] == 'A':
                reorder_count += 1
                stock_status = 'REORDER URGENT' if risk == 'HIGH' else 'REORDER'
            else:
                stock_status = 'STABLE'

            if risk == 'HIGH':
                high_risk_count += 1

            total_forecast_qty += fc['forecast_qty']
            total_forecast_cost += fc['inventory']['forecast_cost']

            products_report.append({
                "product": p_name,
                "abc": row['ABC'],
                "xyz": row['XYZ'],
                "abc_xyz": row['ABC_XYZ'],
                "historical_qty": float(row['TotalQty']),
                "total_sales_val": float(row['TotalValue']),
                "unit_price": float(row['AvgUnitPrice']),
                "avg_daily_demand": fc['avg_daily_demand'],
                "forecast_qty": fc['forecast_qty'],
                "metrics": fc['metrics'],
                "safety_stock": fc['inventory']['safety_stock'],
                "reorder_point": fc['inventory']['reorder_point'],
                "recommended_roq": roq,
                "forecast_cost": fc['inventory']['forecast_cost'],
                "stock_risk": risk,
                "stock_status": stock_status
            })

        overview = {
            "total_products": len(products_report),
            "total_forecast_qty": float(round(total_forecast_qty, 2)),
            "total_forecast_cost": float(round(total_forecast_cost, 2)),
            "reorder_count": reorder_count,
            "high_risk_count": high_risk_count,
            "abc_summary": abc_xyz_df['ABC'].value_counts().to_dict(),
            "xyz_summary": abc_xyz_df['XYZ'].value_counts().to_dict(),
            "lead_time_days": lead_time,
            "service_level": service_level,
            "forecast_days": forecast_days
        }

        return {
            "overview": overview,
            "products": products_report
        }
