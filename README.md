# 🚀 CurbOps: Parking enforcement intelligence: Repo Structure & Dashboard Handoff

*This document outlines exactly what needs to be pushed to your final GitHub repository for the Gridlock 2.0 submission, followed by crucial instructions for your UI/Dashboard team.*

---

## 📁 1. What to Push to the Final Repository

To ensure a clean, professional submission that the judges can easily review, structure your repository exactly like this:

```text
CurbOps/
│
├── README.md                           # Project overview, setup, and submission links
├── .gitignore                          # Ignore raw CSVs, API keys, Python cache, node_modules
│
├── CurbOps_Pipeline/                   # Data Engineering & Spatial Clustering
│   ├── build_cbm_dataset.py            # Stage 1: Data Engineering
│   ├── run_clustering.py               # Stage 2: Spatial Clustering
│   ├── requirements.txt                # Dependencies
│   └── dataset/                        # Processed outputs (version-controlled)
│       ├── zones.geojson               # Map data (2,021 zones)
│       └── zone_summary.json           # Table/Dashboard data
│
├── dashboard/                          # Stage 3 – UI (React + FastAPI)
│   ├── backend/                        # FastAPI server workspace
│   ├── frontend/                       # React app (create‑react‑app or Vite)
│   └── README.md                       # Setup instructions for both backend and frontend
│
├── documentation/                      # Walkthroughs & submission materials
│   ├── pipeline_walkthrough.md         # Full data pipeline explanation
│   ├── clustering_walkthrough.md       # HDBSCAN decisions, challenges, and results
│   └── demo_script.md                  # (To be added) 90‑second demo script
│
├── submission/                         # Final deliverables for the hackathon form
│   ├── pitch_deck.pptx                 # (To be added) 5‑slide presentation
│   ├── screenshots/                    # (To be added) 3 PNGs for the submission
│   └── demo_video.mp4                  # (To be added) 4K backup video
│
└── assets/                             # Logos, banners, or any static assets used in the dashboard
```

---

## 🎨 2. Handoff Notes for the Streamlit Dashboard Team

*Copy and paste the following notes to the developer building your Streamlit UI. It contains critical information about how the data was structured.*

### Dear Dashboard Team:

The Data Engineering and Clustering pipelines are 100% complete. You do not need to run any heavy data processing. **Everything you need is pre-calculated and ready inside `dataset/zones.geojson` and `dataset/zone_summary.json`.**

Here is what you need to know to build the UI:

**1. Rendering the Map (Use PyDeck, NOT Folium)**
There are 2,021 enforcement zones in the GeoJSON. Rendering 2,000 individual markers with Folium will cause the Streamlit app to lag. 
👉 **Solution:** Use Streamlit's native **PyDeck** integration (`st.pydeck_chart`). Use a `ScatterplotLayer` mapped to the `centroid_lon` and `centroid_lat`. 
*Pro-tip:* Use the `radius_m` property from the data to dynamically size the PyDeck circles so judges can see the physical size of the congestion hotspots!

**2. The Data is Already Sorted**
You do not need to use Pandas to sort the data in Streamlit. `zone_summary.json` is **already sorted by `zone_CBM_sum` descending**. The absolute worst, highest-priority hotspots in Bengaluru are at index `[0]`, `[1]`, `[2]`. Just slice `[:5]` to populate your "Top 5 Priorities" UI cards.

**3. Visualizing "Priority Score" vs "CBM"**
*   `zone_CBM_sum` represents the raw, physical blockage impact on traffic. 
*   `priority_score` factors in recurrence (how many days it happens) and peak-hour ratio. 
👉 **Use `priority_score` to assign color codes** on the map (e.g., Top 10% Red = Tier 1 Towing, Next 20% Orange = Tier 2 Clamping).

**4. The "Low Confidence" Flag (Crucial UI Feature)**
Every zone has a `low_confidence` boolean (True/False). If it is `True`, it means this zone had fewer than 5 total violations over 5 months (basically a fluke).
👉 **UI Task:** Add a toggle switch in the Streamlit sidebar: `[x] Hide low-confidence zones`. If checked, filter these out so the police aren't sent to a random spot that only had 2 violations.

**5. The Recommended Patrol Window**
Every zone has a `recommended_window` (e.g., "07:00-08:00" or "19:00-20:00"). Highlight this prominently in your tables. 
*Note:* We wrote a specific algorithm to filter out a massive "night-time batch processing" artifact in the raw BTP data. These window recommendations strictly and accurately target actual daytime morning/evening rush hours.

**6. Formatting the JSON Arrays**
In the JSON, `top_vehicle_types` and `top_violation_types` are nested arrays (e.g., `[{"type": "SCOOTER", "count": 466}]`). 
👉 **UI Task:** Unpack these cleanly into small bar charts or "pill" badges in your UI rather than dumping raw JSON strings to the screen.

Good luck building the dashboard! The data is clean, pre-computed, and ready to go.
