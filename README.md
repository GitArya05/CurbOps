# CurbOps — AI‑Driven Parking Enforcement Intelligence

> **Gridlock 2.0 Hackathon**  
> *Detect illegal parking hotspots · Quantify their impact on traffic flow · Enable targeted enforcement*

CurbOps turns raw police‑violation records into **Capacity‑Blockage Minutes (CBM)** — a single, explainable metric that estimates how much road capacity an illegal parking event destroys. It then clusters violations into 2,021 enforcement zones and presents them on an interactive command‑centre dashboard built for the Bengaluru Traffic Police.

---

## How It Answers the Theme

| Theme Requirement | CurbOps Solution |
|------------------|------------------|
| **Detect illegal parking hotspots** | HDBSCAN density‑based clustering on 115,000+ approved parking violations, with noise filtering and recurrence tracking. |
| **Quantify impact on traffic flow** | `CBM = Duration × Lane‑Blockage Factor × PCE × Junction Sensitivity` — a physics‑informed, fully explainable capacity‑loss metric. |
| **Enable targeted enforcement** | Zones ranked by priority score, assigned **TOW / PATROL / MONITOR** tiers, with a recommended patrol window and the responsible police station. |

---

## Core Innovation: Capacity‑Blockage Minutes (CBM)

\[
\text{CBM} = \text{Duration} \times \text{Lane‑Blockage Factor} \times \text{Vehicle Footprint (PCE)} \times \text{Junction Sensitivity}
\]

- **Duration** – domain‑based defaults (15‑60 min) because `closed_datetime` was 100 % null.
- **Lane‑Blockage Factor** – parsed from the `violation_type` JSON (double‑parking = 1.0, bus‑stop = 0.8, footpath = 0.2…).
- **PCE (Passenger Car Equivalent)** – IRC:106‑inspired vehicle‑size weights (Truck = 3.0, Car = 1.0, Two‑wheeler = 0.3).
- **Junction Sensitivity** – `1 + exp(-distance/100)`; missing junctions are enriched via MapmyIndia reverse‑geocoding.

Zones are sorted by a **priority score** that blends CBM, peak‑hour intensity, and recurrence days. Action tiers are assigned using data‑driven percentiles (top 10% → TOW, next 20% → PATROL, rest → MONITOR).

---

## Dashboard Features

- **Interactive map** with three selectable basemaps — Standard (light), Dark Matter, and Satellite.  
  Zone circles are coloured by tier and sized by real‑world area.
- **Drill‑down panel** — glass‑morphism card showing vehicle‑type charts, violation breakdown, and an auto‑generated explainability sentence.
- **Enforcement Simulation Toggle** — dims low‑priority zones, glows high‑priority ones, and animates a **“CBM Recovered”** counter, illustrating the impact of focusing on only the top 30% of zones.
- **Priority table** — sortable, filterable by police station.
- **Low‑confidence filter** — hides zones with fewer than 5 observations, keeping the map operationally clean.
- **Station filter** — any beat commander can view only their jurisdiction.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Data Processing | Python, Pandas, NumPy |
| Clustering | HDBSCAN (unsupervised ML) |
| Geocoding | MapmyIndia REST API (OAuth 2.0) |
| Backend API | Next.js API Routes (Serverless, zero database latency) |
| Frontend UI | Next.js (React), Tailwind CSS, shadcn/ui |
| Mapping | Leaflet (`react-leaflet`) with CartoDB/Esri tiles |
| Charts | Recharts |

---

## Repository Structure

```text
CurbOps/
├── CurbOps_Pipeline/            # Data Engineering & Clustering
│   ├── build_cbm_dataset.py     # Stage 1 – CBM, MapmyIndia enrichment
│   ├── run_clustering.py        # Stage 2 – HDBSCAN, zone metrics
│   ├── requirements.txt
│   ├── README.md
│   └── dataset/                 # Generated outputs
│       ├── zones.geojson
│       └── zone_summary.json
│
├── dashboard/                   # Next.js Web Dashboard
│   ├── public/                  # Static assets & mapped JSONs
│   ├── src/
│   │   ├── app/api/             # Serverless backend static routes
│   │   └── components/          # React frontend UI
│   ├── package.json
│   ├── tailwind.config.ts
│   └── README.md
│
└── documentation/               # Full project documentation
    ├── README.md                # Documentation index
    ├── architecture_overview.md
    ├── pipeline_walkthrough.md
    ├── clustering_walkthrough.md
    ├── qa_verification_walkthrough.md
    ├── qa_defense.md
    ├── technical_appendix.md
    └── user_guide.md
```

---

## Quick Start

### 1. Data Pipeline
```bash
cd CurbOps_Pipeline
pip install -r requirements.txt
# Place the raw CSV in a 'data/' folder and MapmyIndia secrets in 'secrets.txt'
python build_cbm_dataset.py
python run_clustering.py
```

### 2. Dashboard
```bash
cd dashboard
npm install
npm run dev
# Open http://localhost:3000
```

---

## Documentation Index

| Document | Content |
|----------|---------|
| [`architecture_overview.md`](documentation/architecture_overview.md) | System design & pipeline diagram |
| [`pipeline_walkthrough.md`](documentation/pipeline_walkthrough.md) | CBM calculation, data cleaning, MapmyIndia enrichment |
| [`clustering_walkthrough.md`](documentation/clustering_walkthrough.md) | HDBSCAN logic, noise reassignment, recommended windows |
| [`qa_verification_walkthrough.md`](documentation/qa_verification_walkthrough.md) | Independent pre‑mortem fix verification |
| [`qa_defense.md`](documentation/qa_defense.md) | 10 anticipated judge questions & prepared answers |
| [`technical_appendix.md`](documentation/technical_appendix.md) | Complete formula reference with constants |
| [`user_guide.md`](documentation/user_guide.md) | BTP command‑room operator manual |

---

## Transparency & Data Honesty
We openly document every assumption and limitation:

1. `closed_datetime` is 100 % null → durations are conservative estimates.
2. A night‑batching artifact skews raw timestamps → peak‑hour factor is dampened and enforcement windows are restricted to real morning/evening peaks.
3. The data reflects enforcement patterns, not a census of illegal parking → we mitigate bias by blending multiple signals (CBM, recurrence, junction sensitivity).

*Built in 6 days for the Gridlock 2.0 Hackathon. All code, data choices, and assumptions are transparent and verifiable.*
