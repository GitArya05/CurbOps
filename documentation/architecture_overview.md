# 🏗️ CurbOps: System Architecture & Hotspot Clustering Engine

This document provides a comprehensive A-Z breakdown of how CurbOps transforms 100,000+ raw traffic violations into actionable, prioritized map hotspots on the dashboard.

---

## 1. System Overview: The Decoupled Architecture

CurbOps is designed for maximum performance and zero latency. Instead of running heavy spatial queries in a live database, we split the architecture into two distinct halves:

1. **The Data Engine (Python):** An offline spatial processing pipeline that cleans data, computes impact metrics, and runs machine learning clustering.
2. **The UI Dashboard (Next.js):** A lightweight, static-first frontend that consumes the pre-computed outputs from the Data Engine and renders them interactively on a map.

---

## 2. The Core Logic: Hotspot Detection & CBM

Before we cluster anything, we must understand the *impact* of a violation. A scooter parked for 5 minutes is not the same as a heavy truck parked for 3 hours.

We engineered a custom metric called **CBM (Capacity-Blockage Minutes)**:
**`CBM = Duration × Lane‑Blockage Factor × Vehicle Footprint (PCE) × Junction Sensitivity`**

- **Duration:** Domain‑based defaults (15‑60 min) because the original data had no real clearance timestamps.  
- **Lane‑Blockage Factor:** Parsed from the violation‑type JSON. Double‑parking = 1.0, bus‑stop = 0.8, footpath = 0.2, etc.  
- **Vehicle Footprint:** PCE weights from Indian IRC standards (Truck = 3.0, Car = 1.0, Bike = 0.3).  
- **Junction Sensitivity:** How close the violation is to a major junction (smooth exponential decay, range 1.0‑2.0). Missing junction names were enriched using **MapmyIndia reverse‑geocoding**.

CBM directly answers the theme’s hardest question: *“quantify impact on traffic flow”*.

A zone’s final `priority_score` blends CBM with peak‑hour intensity and recurrence:
`priority_score = zone_CBM_sum × peak_hour_ratio × log(1 + recurrence_days)`

*(peak_hour_ratio is dampened to account for a known night‑batching artifact in the timestamps, ensuring recommendations stay reliable.)*

---

## 3. Spatial Clustering: How We Find The Hotspots

We use an advanced machine learning algorithm called **HDBSCAN (Hierarchical Density-Based Spatial Clustering of Applications with Noise)** to group violations into realistic "Enforcement Zones".

### Why HDBSCAN?
*   **No Pre-defined Zones:** We don't guess how many hotspots exist (unlike K-Means). The algorithm mathematically discovers areas of high density.
*   **Haversine Distance:** We use Earth's actual curvature (Haversine metric in radians) to ensure clusters are physically accurate in meters.
*   **Noise Filtering:** If a car is parked illegally in a random, isolated area, HDBSCAN classifies it as "noise" (`cluster -1`) and discards it. This guarantees the dashboard only shows *systemic, recurring problem areas*, not one-off events.

### The Algorithm Steps:
1. **Cluster Generation:** Groups violations that occur within strict proximity (`min_cluster_size=10`).
2. **Radius Calculation:** Computes the centroid and the maximum Haversine distance to any point in the cluster → `radius_m`.
3. **Priority Scoring:** Sums the CBM of all violations in the zone and blends it with peak‑hour ratio and recurrence days to produce the `priority_score`.

---

## 4. The Handshake: From Backend to Frontend

The Python engine generates two static files:
- `zones.geojson` – Point features with centroid, radius, and all metrics.
- `zone_summary.json` – Array of zones pre‑sorted by `priority_score`.

A lightweight **Next.js API backend** loads these files into memory at startup and serves them via internal endpoints (e.g., `/api/zones` and `/api/zones/geojson`).

The **Next.js + Tailwind** frontend fetches these endpoints once and never touches a database. Result: **zero‑latency dashboard**.

---

## 5. The Map UI: Visualizing the Data

The dashboard uses **Leaflet (`react-leaflet`)** to render the interactive map. Here is how the clustering data controls the UI:

*   **Dynamic Sizing:** The GeoJSON dictates the size of the circles on the map. A massive intersection cluster with a 150m radius will draw a proportionally massive circle on the map.
*   **Action Tiers:** Zones are categorized based on their `priority_score` (a composite of CBM, peak‑hour intensity, and recurrence) using data‑driven percentiles: 🔴 **TOW** (top 10%), 🟠 **PATROL** (next 20%), and 🔵 **MONITOR** (rest).

### 🔥 Enforcement Impact Simulation (Killer Feature)
A toggle switch in the sidebar activates **“Simulate Optimized Enforcement”**. The map instantly shows what happens if BTP focuses only on the top 30% of zones:

- Low‑priority zones (MONITOR) dim to 30% opacity.
- High‑priority zones (TOW + PATROL) keep full colour and receive a subtle glow.
- The city‑wide CBM counter **animates down** to the estimated remaining CBM.
- A second counter appears: **“Estimated CBM Recovered: XX,XXX minutes”** with a count‑up animation.
- A small label notes it’s an *illustrative simulation (assumes 40% impact reduction in prioritized zones)*.

This toggle doesn’t just show a static problem – it **proves the operational value** of focused enforcement in one motion.

### Additional Dashboard Intelligence
- **Station Filter:** Drop‑down lets any beat commander see only their zones.
- **Low‑Confidence Toggle:** Hides zones with <5 observations, keeping the map operationally clean.
- **Drill‑Down Panel:** Click a zone → glass‑morphism panel with vehicle pie charts, violation bar charts, and an auto‑generated explainability sentence.
- **Honest Data Handling:** We clearly document the assumptions (missing timestamps, default durations, timestamp artifacts) so the tool is transparent and defensible in Q&A.
