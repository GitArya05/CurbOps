import pandas as pd

df = pd.read_csv("dataset/violations_with_cbm.csv")

# 1. Row count
print(f"Rows: {len(df):,}  (expected ~115k)")

# 2. Columns
required = ['duration_min','lane_blockage_factor','pce','junction_sensitivity','cbm']
missing = [c for c in required if c not in df.columns]
print(f"Missing columns: {missing or 'None'}")

# 3. Nulls
print(f"Null values:\n{df[required].isnull().sum()}")

# 4. Value ranges
print(f"duration_min: {df.duration_min.min()}-{df.duration_min.max()}  (expect 15-60)")
print(f"lane_blockage: {df.lane_blockage_factor.min()}-{df.lane_blockage_factor.max()}  (expect 0.2-1.0)")
print(f"pce: {df.pce.min()}-{df.pce.max()}  (expect 0.2-3.0)")
print(f"junction_sens: {df.junction_sensitivity.min()}-{df.junction_sensitivity.max()}  (expect 1.0-2.0)")
print(f"cbm: {df.cbm.min():.1f}-{df.cbm.max():.1f}  (mean ~13.9)")

# 5. Top 5 stations by total CBM (sanity)
top = df.groupby('police_station')['cbm'].sum().sort_values(ascending=False).head(5)
print(f"\nTop 5 stations by total CBM:\n{top}")
