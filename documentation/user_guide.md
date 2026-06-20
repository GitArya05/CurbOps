# 📖 CurbOps User Guide — BTP Command Room

*How to turn parking‑violation data into targeted enforcement actions.*

---

## 1. What CurbOps Does

CurbOps shows you **where illegal parking is hurting traffic the most** and
**what to do about it**.

Instead of a passive heatmap, you see **enforcement zones** — real areas where
a patrol or a tow‑truck can make an immediate difference. Every zone comes
with a recommended action, a time window, and the police station responsible.

---

## 2. Opening the Dashboard

1. Open your web browser (Chrome, Firefox, or Edge).
2. Go to the address provided by your IT team.  
   *(Typically `http://localhost:3000` when running locally, or a secure
   department URL.)*
3. The dashboard loads in under a second. No login is required – the system
   is designed for the command‑room terminal.

---

## 3. Screen Layout

![Dashboard layout](screenshots/full_dashboard.png)

| Area | What you see |
| :--- | :--- |
| **Left sidebar** (dark) | City‑wide statistics, filter controls, and navigation tabs. |
| **Main map** | Full‑screen Bengaluru map with coloured **enforcement zone circles**. |
| **Drill‑down panel** (appears on click) | Detailed information about a selected zone. |
| **Priority Table** (switch via sidebar) | A sortable list of every zone, ranked by urgency. |

---

## 4. Understanding the Map

### 4.1 Zone Circles
Each circle is an **enforcement zone** — a group of repeated illegal‑parking
violations.

- **Circle colour** = action priority (see §4.2).  
- **Circle size** = physical area of the zone. A large circle means the problem
  is spread out; a small, tight circle is usually a single junction or hotspot.  
- **Hover** over any circle to see the junction name, the estimated capacity
  impact (CBM), and the recommended patrol window.

### 4.2 Action Tiers (Colour Legend)

| Colour | Tier | Meaning |
| :--- | :--- | :--- |
| 🔴 **Crimson** | **TOW** | Highest impact. Dispatch a tow‑truck immediately within the recommended window. |
| 🟠 **Amber** | **PATROL** | Medium impact. Send an officer for ticketing / drive‑by clearing. |
| 🔵 **Slate** | **MONITOR** | Lower impact. Keep under CCTV observation; no physical deployment today. |

### 4.3 What the Numbers Mean
- **CBM (Capacity‑Blockage Minutes):** estimated road‑capacity lost due to
  illegal parking in that zone. Higher CBM → more severe congestion.  
- **Priority Score:** blends CBM with how often violations happen during peak
  hours and over many days. The top‑ranked zones are the ones where you can
  recover the most capacity fastest.

---

## 5. Taking Action: The Drill‑Down Panel

When you **click** a zone circle, a detailed panel slides in from the right.

### 5.1 What’s inside
- **Zone name** (e.g., “Elite Junction” or “Unnamed Zone #284”).
- **Tier badge** (TOW / PATROL / MONITOR) – the action you should take.
- **Four key numbers:** Total CBM, Violation Count, Peak‑Hour %, Recurrence
  Days.
- **Recommended Action box** (teal): shows the best patrol window (e.g.,
  “07:00‑08:00”) and the police station responsible.
- **Charts:** pie chart of top violation types (WRONG PARKING, NO PARKING,
  etc.) and bar chart of vehicle types (scooter, car, truck…).
- **Explainability sentence:** one line that tells you *why* this zone is
  ranked high.

### 5.2 What to do with the information
1. Read the **recommended window**.  
2. Check the **police station** — make sure an officer from that station is
   available.  
3. Look at the **vehicle mix** — if it’s mostly heavy vehicles, you may need
   a tow‑truck; if it’s scooters, a patrol officer may be enough.  
4. Close the panel (× button) to return to the full map.

---

## 6. Using the Sidebar Controls

### 6.1 Station Filter
The dropdown at the top of the sidebar lets you filter the map and table to
**only your beat**. Select your station (e.g., “Upparpet”) and everything
updates instantly.

### 6.2 Hide Low‑Confidence Zones
This toggle (default ON) removes zones that have fewer than 5 recorded
violations. These are statistically weak spots — keep the toggle ON to avoid
noise.

### 6.3 Simulate Optimized Enforcement (🔥 Important)
This toggle shows you **what happens if you focus only on the top 30% of
zones**.

**When ON:**
- The map dims low‑priority (MONITOR) zones.
- High‑priority zones (TOW + PATROL) get a glow.
- The city‑wide CBM counter drops to show the **estimated remaining impact**.
- A second counter appears: **“Estimated CBM Recovered: X,XXX minutes”**.

This is a simulation that assumes a 40% reduction in congestion when you
clear a prioritized zone. Use it to explain to supervisors *why* you need
resources at a specific time.

### 6.4 Switching to the Priority Table
Click the **“Priority Table”** tab in the sidebar. The map is replaced by a
full‑width table listing all zones, sorted by priority score.

- Click any column header to sort by that metric (CBM, peak‑hour %, etc.).
- Click a row to jump back to the map with that zone’s drill‑down open.
- The table respects the same station filter and low‑confidence toggle.

---

## 7. Typical Daily Workflow

### 7.1 Morning Briefing (5 minutes)
1. Open CurbOps.
2. Leave the station filter on “All” to see the city‑wide situation.
3. Look at the **red circles** on the map — these are your TOW priorities.
4. Check their recommended windows. Are any falling in the next shift?

### 7.2 Resource Allocation
1. Switch the station filter to your beat.
2. Note the top 3 PATROL zones and their windows.
3. Assign officers accordingly. For TOW zones, check tow‑truck availability.
4. Use the **Simulate Optimized Enforcement** toggle to show your commander
   the estimated capacity recovery if the plan is executed.

### 7.3 After Enforcement
- The data is updated when a new CSV is ingested (typically overnight).  
- The next morning, the map reflects the updated situation. Over time,
  recurring TOW zones that are consistently cleared should drop in rank —
  a sign that enforcement is working.

---

## 8. Important Notes

- **All data is estimated.** The tool uses conservative assumptions for
  parking duration because real clearance times are not available. The
  recommended windows are based on available timestamps and are meant as
  guidance, not an absolute guarantee.
- **The map shows historical patterns** (Jan–May 2026). Sudden events
  (VIP movements, festivals, market days, or road closures) may create new
  temporary parking hotspots that are not yet reflected in the historical data.
- **Enforcement bias:** The dataset reflects where police have historically
  patrolled. CurbOps mitigates this by blending multiple factors (capacity
  loss, recurrence, junction importance) rather than just counting tickets.
- **Always verify with on‑ground intelligence.** The dashboard is a decision‑
  support tool; the final call rests with the commanding officer.

---

*For technical questions or to request a data refresh, contact the IT support
team. Built with ❤️ for Gridlock 2.0 Hackathon.*
