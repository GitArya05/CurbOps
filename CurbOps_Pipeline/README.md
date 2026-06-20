# 🚀 CurbOps: Parking Enforcement Intelligence – Backend Pipeline

> **Gridlock 2.0 Hackathon** | Data Engineering & Spatial Clustering Engine

The **CurbOps** backend pipeline transforms raw traffic‑violation records into
**Capacity‑Blockage Minutes (CBM)** and groups them into actionable
enforcement zones. The dashboard consumes its two static outputs:
`zones.geojson` and `zone_summary.json`.

---

## 📂 Repository Structure

```text
CurbOps_Pipeline/
├── README.md
├── requirements.txt
├── build_cbm_dataset.py       # Stage 1 – CBM computation & data enrichment
├── run_clustering.py          # Stage 2 – HDBSCAN clustering & zone metrics
└── dataset/                   # Generated outputs (ready for the dashboard)
    ├── zones.geojson
    └── zone_summary.json
```

*Note: The raw input CSV and intermediate `violations_with_cbm.csv` are not
committed due to size; they are generated locally.*

---

## ⚙️ Prerequisites

- **Python 3.10+**
- A **MapmyIndia OAuth2 key pair** (Client ID & Secret) stored in a file
  named `secrets.txt` in the project root (line 1 = Client ID, line 2 = Secret).
- The raw dataset `jan to may police violation_anonymized791b166.csv` placed
  in a `data/` folder (the path can be changed inside the script).

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 🧪 How to Run

### Step 1 – Compute CBM
```bash
python build_cbm_dataset.py
```
Loads and cleans ~298k rows → 115,400 approved parking violations.
Parses violation‑type JSON, assigns realistic durations, maps vehicle types
to PCE, and enriches missing junction names via MapmyIndia
reverse‑geocoding (results cached in `dataset/mmi_cache.json`).
Outputs `dataset/violations_with_cbm.csv` (≈49 MB).

### Step 2 – Cluster into Enforcement Zones
```bash
python run_clustering.py
```
Clusters violations with HDBSCAN (Haversine metric, `min_cluster_size=10`).
Reassigns noise points within 200 m, computes per‑zone metrics (CBM sum,
vehicle/violation type breakdown, recommended patrol window, action tier).

Generates the two final artifacts:
*   `dataset/zones.geojson` – GeoJSON FeatureCollection (2,021 zones)
*   `dataset/zone_summary.json` – sorted array of zone objects

---

## 📊 Core Metrics Explained

### CBM (Capacity‑Blockage Minutes)
```text
CBM = Duration × Lane‑Blockage Factor × PCE × Junction Sensitivity
```
*   **Duration** – domain‑based defaults (15‑60 min) because `closed_datetime` was 100 % null.
*   **Lane‑Blockage Factor** – extracted from the `violation_type` JSON array (double‑parking = 1.0, bus‑stop = 0.8, footpath = 0.2, etc.).
*   **PCE (Passenger Car Equivalent)** – Indian IRC‑inspired weights (Truck = 3.0, Car = 1.0, Two‑wheeler = 0.3).
*   **Junction Sensitivity** – `1 + exp(-distance_m / 100)`; missing junction names are resolved via MapmyIndia.

### Priority Score
```text
priority_score = zone_CBM_sum × safe_peak_factor × log(1 + recurrence_days)
where safe_peak_factor = 0.5 + 0.5 × peak_hour_ratio
```
The dampened peak factor accounts for a known night‑batching artifact
(>70k violations timestamped between midnight‑6 AM). Zones are sorted by
`priority_score` and assigned action tiers via percentiles.

---

## 🎛️ Tunable Parameters

All key constants are declared at the top of `run_clustering.py`:

| Constant | Default | Description |
| :--- | :--- | :--- |
| `MIN_CLUSTER_SIZE` | `10` | Minimum violations to form a zone |
| `CLUSTER_SELECTION_EPSILON` | `0.0` | No forced merging of clusters |
| `NOISE_REASSIGN_THRESHOLD_M` | `200` | Max distance to adopt a noise point |
| `LOW_CONFIDENCE_THRESHOLD` | `5` | Flag zones with fewer than 5 violations |

*Action tier cut‑offs (90ᵗʰ / 70ᵗʰ percentiles of priority_score) are also configurable inside the script.*

---

## 📤 Output Files

| File | Content |
| :--- | :--- |
| `dataset/zones.geojson` | Point features with centroid, `radius_m`, and properties (CBM, tier, vehicle/violation breakdowns, recommended window, etc.). |
| `dataset/zone_summary.json` | The same zones as a JSON array, sorted by `priority_score` descending. Used directly by the dashboard’s priority table. |

---

## 🔍 Data Limitations & Transparency

We are upfront about the dataset’s shortcomings so that the tool stays defensible in Q&A:

*   **No real clearance timestamps** – `closed_datetime` is 100 % null. Durations are conservative, violation‑type‑based defaults.
*   **Night‑batching artifact** – Timestamps cluster unnaturally between 00:00‑06:00 due to batch processing. Our peak‑hour factor is dampened and the recommended enforcement window is restricted to true morning/evening peak hours.
*   **Enforcement bias** – The data reflects where police patrol, not all illegal parking. We mitigate this by blending CBM, recurrence, and junction sensitivity rather than relying on raw ticket counts.

Built with ❤️ by the CurbOps Team for Gridlock 2.0
