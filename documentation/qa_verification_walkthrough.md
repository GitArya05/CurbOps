# 🛡️ CurbOps: QA Verification Walkthrough

> **Role:** Quality-Assurance Auditor
> **Objective:** Verify that all critical fixes requested by the hackathon judges have been successfully implemented across the codebase and output datasets.

This document serves as the official QA audit trail for the CurbOps Backend Pipeline. 

---

## 🔍 Audit Checklist & Findings

### 1. MapmyIndia Enrichment 
**Status: PASS ✅**
*   **Inspection:** Reviewed `CurbOps_Pipeline/build_cbm_dataset.py`.
*   **Verification:** The code successfully requests the MapmyIndia OAuth token and queries the Reverse Geocode API. Crucially, the logic merges the returned `name` directly into the `junction_name` column and recomputes the Haversine distance using the newly resolved `latitude` and `longitude` coordinates.

### 2. Priority Score Dampening against Timestamp Artifacts
**Status: PASS ✅**
*   **Inspection:** Reviewed `CurbOps_Pipeline/run_clustering.py`.
*   **Verification:** Located the `priority_score` calculation within `compute_zone_metrics()`. The logic correctly utilizes the dampened formula `safe_peak_factor = 0.5 + 0.5 * peak_hour_ratio` to mitigate the impact of overnight batch-processing anomalies.

### 3. Recommended Window Documentation
**Status: PASS ✅**
*   **Inspection:** Reviewed `documentation/clustering_walkthrough.md`.
*   **Verification:** The documentation accurately reflects the updated implementation. It explicitly outlines that the `recommended_window` prioritizes the 7-10 AM and 5-7 PM rush hours, and clearly documents the batch-artifact caveat justifying this logic.

### 4. Action Tiers (TOW/PATROL/MONITOR) in Outputs
**Status: FAIL ❌**
*   **Inspection:** Reviewed `CurbOps_Pipeline/dataset/zone_summary.json` and `CurbOps_Pipeline/dataset/zones.geojson`.
*   **Verification:** While the logic to assign `action_tier` exists in the Python script, the actual JSON and GeoJSON outputs completely lack the `action_tier` field. 

### 5. Zones Sorted by Priority Score
**Status: FAIL ❌**
*   **Inspection:** Reviewed `CurbOps_Pipeline/dataset/zone_summary.json`.
*   **Verification:** The `run_clustering.py` script correctly sorts by `priority_score` descending. However, the `zone_summary.json` file is currently sorted by `zone_CBM_sum`.

### 6. Hardcoded Credentials Removed
**Status: PASS ✅**
*   **Inspection:** Reviewed `CurbOps_Pipeline/build_cbm_dataset.py`.
*   **Verification:** No plaintext API keys are present. The script safely loads `CLIENT_ID` and `CLIENT_SECRET` via a local, git-ignored `secrets.txt` file or via system environment variables (`MAPPLS_CLIENT_ID` / `MAPPLS_CLIENT_SECRET`).

---

## 🚨 Critical QA Conclusion & Next Steps

**The Code is Correct, but the Artifacts are Stale.**
The failures in Check 4 and Check 5 are **not** due to missing logic. The Python scripts (`build_cbm_dataset.py` and `run_clustering.py`) are perfectly written and contain all the requested fixes. 

The issue is simply that **the pipeline was never re-executed** after the code changes were saved. As a result, the `dataset/` folder contains stale JSON files from a previous run.

**Resolution Required:**
1. Execute `python CurbOps_Pipeline/run_clustering.py` to regenerate the outputs.
2. Commit and push the freshly generated JSON and GeoJSON files to the repository.
