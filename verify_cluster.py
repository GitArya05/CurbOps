import json

# 1. GeoJSON
with open("dataset/zones.geojson", "r", encoding="utf-8") as f:
    geojson = json.load(f)
print(f"GeoJSON features: {len(geojson['features'])}")
print(f"First feature geometry type: {geojson['features'][0]['geometry']['type']}")
print(f"First feature properties keys: {list(geojson['features'][0]['properties'].keys())}")

# 2. Zone summary
with open("dataset/zone_summary.json", "r", encoding="utf-8") as f:
    zones = json.load(f)
print(f"\nZone summary records: {len(zones)}")
print(f"First zone CBM: {zones[0]['zone_CBM_sum']}")
print(f"First zone window: {zones[0]['recommended_window']}")
print(f"Zones sorted by CBM descending: {all(zones[i]['zone_CBM_sum'] >= zones[i+1]['zone_CBM_sum'] for i in range(len(zones)-1))}")