# ⚙️ CurbOps — Technical Appendix

*Gridlock 2.0 Hackathon · CausaFlow AI*  
*All formulas, constants, data‑processing rules, and design decisions documented here can be verified in the source code.*

---

## 1. CBM (Capacity‑Blockage Minutes)

\[
\text{CBM} = D \times B \times P \times J
\]

| Symbol | Name | Meaning |
| :--- | :--- | :--- |
| \(D\) | Duration (min) | Estimated time the vehicle blocked the road. |
| \(B\) | Lane‑Blockage Factor | Severity of the obstruction (0–1). |
| \(P\) | Passenger Car Equivalent (PCE) | Vehicle size weight per IRC:106. |
| \(J\) | Junction Sensitivity | Proximity multiplier (1.0–2.0). |

---

## 2. Duration (\(D\))

The raw dataset has **100 % null `closed_datetime`**, so duration must be assigned using domain‑knowledge defaults.

| Violation Type Keyword | Duration (min) |
| :--- | :--- |
| `double park`, `double parking` | 15 |
| `bus stop` | 20 |
| `wrong parking`, `no parking` | 45 |
| `footpath`, `parking on footpath` | 60 |
| Other / unknown | 30 |

All values are capped at **240 minutes**. These defaults are explicitly labelled as **estimates**, not physical measurements.

---

## 3. Lane‑Blockage Factor (\(B\))

Extracted from the `violation_type` JSON array. When multiple types exist on one row, the **maximum** factor is taken.

| Violation Type Keyword | Factor |
| :--- | :--- |
| `double park`, `double parking` | 1.0 |
| `bus stop`, `bus‑stop parking` | 0.8 |
| `wrong parking`, `no parking`, `no‑parking zone` | 0.4 |
| `footpath`, `parking on footpath` | 0.2 |
| Unknown / other | 0.4 |

---

## 4. Passenger Car Equivalent (\(P\))

Mapped from the 22 raw `vehicle_type` strings using IRC:106‑inspired values.

| Vehicle Type | PCE |
| :--- | :--- |
| Truck, HGV, Bus | 3.0 |
| LCV, MAXI‑CAB, Goods Auto | 2.0 |
| Car, Jeep, Van | 1.0 |
| Passenger Auto, Auto‑rickshaw | 0.5 |
| Motor Cycle, Scooter, Bike | 0.3 |
| Bicycle | 0.2 |
| Unmatched | 1.0 (default) |

---

## 5. Junction Sensitivity (\(J\))

### 5.1 Distance to Junction
For every violation, the distance to the nearest major junction is computed using the **Haversine formula** (Earth radius = 6 371 000 m).

- If the CSV contains a valid `junction_name`, the distance is calculated to that junction’s coordinates (obtained from a lookup built from the data itself).
- If `junction_name` is missing or “No Junction”, the **MapmyIndia Reverse‑Geocode API** (OAuth 2.0) is called to resolve the nearest junction/landmark. Results are cached in `dataset/mmi_cache.json` for future runs.

### 5.2 Sensitivity Formula

\[
J = 1 + \exp\left(-\frac{d}{100}\right)
\]

Where \(d\) = distance in metres.  
Range: **1.0** (far away) to **2.0** (directly at the junction). No cliff‑edge threshold.

---

## 6. Priority Score

Each enforcement zone (cluster) receives a composite priority score that blends impact magnitude, peak‑hour intensity, and persistence.

\[
\text{priority\_score} = S_{\text{CBM}} \times f_{\text{peak}} \times \ln(1 + R)
\]

| Symbol | Meaning |
| :--- | :--- |
| \(S_{\text{CBM}}\) | Sum of `cbm` for all violations in the zone. |
| \(f_{\text{peak}}\) | Dampened peak‑hour factor (see below). |
| \(R\) | Recurrence days (unique calendar dates in the zone). |

### 6.1 Dampened Peak‑Hour Factor
The raw `peak_hour_ratio` is computed as the fraction of violations whose `created_datetime` hour falls within **PEAK_HOURS** = {7,8,9,10,17,18,19} (IST).  
Because the dataset contains a **night‑batching artifact** (>70k rows stamped 00:00–06:00), the ratio is artificially low for many zones. We therefore dampen it:

\[
f_{\text{peak}} = 0.5 + 0.5 \times \text{peak\_hour\_ratio}
\]

This keeps the factor in the range **[0.5, 1.0]**, ensuring no zone is zeroed out by the artifact while still rewarding genuine peak‑hour intensity.

---

## 7. Action Tiers

Zones are ranked by `priority_score` (descending). Enforcement tiers are assigned using **data‑driven percentiles**, not arbitrary cut‑offs.

| Percentile | Tier | Display Colour |
| :--- | :--- | :--- |
| ≥ 90th | **TOW** | Crimson (#E5484D) |
| 70th–89th | **PATROL** | Amber (#E8A33D) |
| < 70th | **MONITOR** | Slate (#5B6B7C) |

These thresholds are computed dynamically each time `run_clustering.py` is executed.

---

## 8. HDBSCAN Clustering Parameters

| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| `min_cluster_size` | 10 | Empirically yields 2 021 zones – granular enough for targeted enforcement, not fragmented noise. |
| `metric` | `haversine` | Accounts for Earth’s curvature when computing distances between lat/lon points. |
| `cluster_selection_epsilon` | 0.0 | No forced merging; lets HDBSCAN discover natural density boundaries. (0.001 rad ≈ 6.4 km, which collapsed the city into 2 mega‑clusters – a bug we caught and fixed.) |
| `allow_single_cluster` | False | Forces the algorithm to find multiple distinct zones. |

All constants are declared at the top of `run_clustering.py` and are **tunable**.

---

## 9. Noise Reassignment

Points classified as noise (`zone_id = -1`) are not simply discarded.  
We compute the Haversine distance from each noise point to every cluster centroid.  
If the **minimum distance ≤ 200 m**, the noise point is adopted into that cluster.  
Remaining noise is dropped. This process recovered **29 653** points (out of 32 552 noise) and left only 2 899 true outliers.

---

## 10. Recommended Enforcement Window

The `recommended_window` is the one‑hour interval with the highest violation count **within** defined peak hours (`PEAK_HOURS`).  
If a zone has **zero** violations during those hours, it falls back to the global maximum hour. This logic prevents recommending patrols at 03:00–04:00 due to the night‑batching artifact.

---

## 11. Data Handling & Transparency

- **Missing `closed_datetime`:** 100 % null → domain‑default durations used (Section 2). Clearly labelled as estimates.
- **Night‑batching artifact:** Over 70k violations timestamped 00:00–06:00. We dampen the peak‑hour factor (Section 6.1) and force the recommended window into real peak hours (Section 10).
- **Enforcement bias:** The data reflects where police patrol. We mitigate by using multi‑factor scoring (CBM, recurrence, junction sensitivity) rather than raw counts, and by openly documenting the limitation.
- **Low‑confidence flag:** Zones with < 5 violations are flagged (`low_confidence = true`). The dashboard hides them by default.

---

## 12. Output File Specifications

### 12.1 `dataset/zones.geojson`
- **Type:** GeoJSON FeatureCollection
- **Geometry:** `Point` at `[centroid_lon, centroid_lat]`
- **Properties per feature:**  
  `zone_id`, `zone_CBM_sum`, `violation_count`, `peak_hour_ratio`, `recurrence_days`,  
  `top_vehicle_types` (array of `{type, count}`), `top_violation_types` (array of `{type, count}`),  
  `centroid_lat`, `centroid_lon`, `dominant_junction`, `police_station`,  
  `recommended_window` (string), `radius_m`, `priority_score`, `low_confidence` (bool), `action_tier` (string).

### 12.2 `dataset/zone_summary.json`
- **Type:** JSON array of zone objects (same properties as GeoJSON, plus `zone_id`).
- **Sort order:** `priority_score` descending.

Both files are loaded by the **Next.js API backend** and consumed by the **React dashboard frontend**.

---

## 13. References

- IRC:106‑1990 – *Guidelines for Capacity of Urban Roads in Plain Areas* (Indian Roads Congress).
- IRC:SP:41‑1994 – *Guidelines for the Design of At‑Grade Intersections in Rural & Urban Areas*.
- Indo‑HCM concepts for lane‑blockage estimation.
- HDBSCAN: McInnes, L., Healy, J., & Astels, S. (2017). *hdbscan: Hierarchical density based clustering.* Journal of Open Source Software.

---

*Every formula, parameter, and assumption listed here can be traced to the source code in `build_cbm_dataset.py` and `run_clustering.py`.*
