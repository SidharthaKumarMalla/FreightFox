import pandas as pd
import numpy as np

df = pd.read_csv('shipments.csv')

print("=== SHAPE ===")
print(df.shape)

print("\n=== DTYPES ===")
print(df.dtypes)

print("\n=== NULL COUNTS ===")
print(df.isnull().sum())

print("\n=== UNIQUE VALUES ===")
for col in ['region', 'mode', 'carrier_id', 'status', 'origin_city', 'destination_city']:
    print(f"{col}: {df[col].nunique()} -> {sorted(df[col].dropna().unique())}")

print("\n=== STATUS DISTRIBUTION ===")
print(df['status'].value_counts())

print("\n=== REGION DISTRIBUTION ===")
print(df['region'].value_counts())

print("\n=== CUSTOMER COUNT ===")
print(df['customer_id'].nunique())

print("\n=== FREIGHT COST STATS ===")
print(df['freight_cost'].describe())

print("\n=== DISTANCE STATS ===")
print(df['distance_km'].describe())

# Date parsing
for col in ['booking_date', 'pickup_date', 'delivery_date', 'promised_delivery_date', 'actual_delivery_date']:
    df[col] = pd.to_datetime(df[col], errors='coerce')

print("\n=== DATE NULLS AFTER PARSING ===")
date_cols = ['booking_date', 'pickup_date', 'delivery_date', 'promised_delivery_date', 'actual_delivery_date']
for col in date_cols:
    print(f"{col}: {df[col].isnull().sum()} nulls")

# On-time analysis
df['delay_days'] = (df['actual_delivery_date'] - df['promised_delivery_date']).dt.days
df['is_late'] = df['delay_days'] > 0

print("\n=== ON-TIME PERFORMANCE BY REGION ===")
delivered = df[df['actual_delivery_date'].notna()]
region_perf = delivered.groupby('region').agg(
    total=('shipment_id', 'count'),
    late=('is_late', 'sum'),
    avg_delay=('delay_days', 'mean')
).assign(late_pct=lambda x: x['late'] / x['total'] * 100)
print(region_perf.sort_values('late_pct', ascending=False))

print("\n=== ON-TIME PERFORMANCE BY CARRIER ===")
carrier_perf = delivered.groupby('carrier_id').agg(
    total=('shipment_id', 'count'),
    late=('is_late', 'sum'),
    avg_delay=('delay_days', 'mean')
).assign(late_pct=lambda x: x['late'] / x['total'] * 100)
print(carrier_perf.sort_values('late_pct', ascending=False))

print("\n=== ON-TIME PERFORMANCE BY REGION x CARRIER ===")
rc_perf = delivered.groupby(['region', 'carrier_id']).agg(
    total=('shipment_id', 'count'),
    late=('is_late', 'sum'),
    avg_delay=('delay_days', 'mean')
).assign(late_pct=lambda x: x['late'] / x['total'] * 100)
print(rc_perf.sort_values('late_pct', ascending=False).head(20))

print("\n=== FREIGHT COST vs DISTANCE CORRELATION ===")
print(f"Pearson correlation: {df['freight_cost'].corr(df['distance_km']):.4f}")

print("\n=== COST PER KM BY CARRIER ===")
df['cost_per_km'] = df['freight_cost'] / df['distance_km']
carrier_cost = df.groupby('carrier_id').agg(
    avg_cost=('freight_cost', 'mean'),
    avg_distance=('distance_km', 'mean'),
    avg_cost_per_km=('cost_per_km', 'mean'),
    median_cost_per_km=('cost_per_km', 'median'),
    count=('shipment_id', 'count')
)
print(carrier_cost.sort_values('avg_cost_per_km', ascending=False))

print("\n=== CUSTOMER DELAY ANALYSIS (TOP 15) ===")
cust_delay = delivered.groupby('customer_id').agg(
    total=('shipment_id', 'count'),
    late=('is_late', 'sum'),
    avg_delay=('delay_days', 'mean')
).assign(late_pct=lambda x: x['late'] / x['total'] * 100)
print(cust_delay.sort_values('late_pct', ascending=False).head(15))

print("\n=== WORST CUSTOMERS - CARRIER BREAKDOWN ===")
worst_custs = cust_delay.sort_values('late_pct', ascending=False).head(5).index
for cust in worst_custs:
    cust_data = delivered[delivered['customer_id'] == cust]
    print(f"\n--- {cust} ---")
    print(cust_data.groupby('carrier_id').agg(
        total=('shipment_id', 'count'),
        late=('is_late', 'sum'),
        avg_delay=('delay_days', 'mean')
    ).assign(late_pct=lambda x: x['late'] / x['total'] * 100))

print("\n=== WORST CUSTOMERS - REGION BREAKDOWN ===")
for cust in worst_custs:
    cust_data = delivered[delivered['customer_id'] == cust]
    print(f"\n--- {cust} ---")
    print(cust_data.groupby('region').agg(
        total=('shipment_id', 'count'),
        late=('is_late', 'sum'),
        avg_delay=('delay_days', 'mean')
    ).assign(late_pct=lambda x: x['late'] / x['total'] * 100))

print("\n=== DATA QUALITY CHECKS ===")
# Negative distances
print(f"Negative distances: {(df['distance_km'] < 0).sum()}")
print(f"Zero distances: {(df['distance_km'] == 0).sum()}")
# Negative costs
print(f"Negative freight costs: {(df['freight_cost'] < 0).sum()}")
print(f"Zero freight costs: {(df['freight_cost'] == 0).sum()}")
# Delivery before pickup
print(f"Delivery before pickup: {(df['delivery_date'] < df['pickup_date']).sum()}")
# Actual delivery date but status not Delivered
print(f"Has actual_delivery but not Delivered status: {((df['actual_delivery_date'].notna()) & (df['status'] != 'Delivered')).sum()}")
# Delivered but no actual_delivery_date
print(f"Delivered status but no actual_delivery_date: {((df['status'] == 'Delivered') & (df['actual_delivery_date'].isna())).sum()}")
# Same origin and destination
print(f"Same origin/destination city: {(df['origin_city'] == df['destination_city']).sum()}")
# Outlier costs
q1, q3 = df['freight_cost'].quantile(0.25), df['freight_cost'].quantile(0.75)
iqr = q3 - q1
outlier_high = (df['freight_cost'] > q3 + 3 * iqr).sum()
outlier_low = (df['freight_cost'] < q1 - 3 * iqr).sum()
print(f"Freight cost outliers (>3*IQR): high={outlier_high}, low={outlier_low}")
# Duplicate shipment IDs
print(f"Duplicate shipment_ids: {df['shipment_id'].duplicated().sum()}")

print("\n=== MODE DISTRIBUTION BY REGION ===")
print(pd.crosstab(df['region'], df['mode']))

print("\n=== ON-TIME BY MODE ===")
mode_perf = delivered.groupby('mode').agg(
    total=('shipment_id', 'count'),
    late=('is_late', 'sum'),
    avg_delay=('delay_days', 'mean')
).assign(late_pct=lambda x: x['late'] / x['total'] * 100)
print(mode_perf)

# Linear regression for cost vs distance
from numpy.polynomial import polynomial as P
mask = df['freight_cost'].notna() & df['distance_km'].notna() & (df['distance_km'] > 0)
x = df.loc[mask, 'distance_km'].values
y = df.loc[mask, 'freight_cost'].values
coeffs = np.polyfit(x, y, 1)
print(f"\n=== LINEAR FIT: cost = {coeffs[0]:.2f} * distance + {coeffs[1]:.2f} ===")

# Residuals by carrier
df_clean = df[mask].copy()
df_clean['predicted_cost'] = np.polyval(coeffs, df_clean['distance_km'])
df_clean['residual'] = df_clean['freight_cost'] - df_clean['predicted_cost']
df_clean['residual_pct'] = df_clean['residual'] / df_clean['predicted_cost'] * 100

print("\n=== CARRIER RESIDUAL ANALYSIS ===")
carrier_residual = df_clean.groupby('carrier_id').agg(
    avg_residual=('residual', 'mean'),
    median_residual=('residual', 'median'),
    avg_residual_pct=('residual_pct', 'mean'),
    count=('shipment_id', 'count')
)
print(carrier_residual.sort_values('avg_residual_pct', ascending=False))
