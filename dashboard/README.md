# 🚦 CurbOps: Parking Enforcement Dashboard

Welcome to the **CurbOps Dashboard**! This is the frontend user interface for the Gridlock 2.0 hackathon submission. 

This dashboard is designed to take the massive, pre-calculated traffic congestion data from our spatial clustering engine and present it to Bengaluru Traffic Police (BTP) as highly actionable, easy-to-read enforcement zones.

---

## 💻 Tech Stack

This project was built from the ground up for speed, aesthetics, and type-safety:

*   **Framework:** Next.js 16 (App Router)
*   **Styling:** Tailwind CSS 4.0
*   **UI Components:** shadcn/ui (Radix Primitives)
*   **Charts:** Recharts
*   **Animations:** Framer Motion
*   **Mapping:** React-Leaflet (with MapmyIndia / Mappls tiles)
*   **State Management:** Zustand
*   **Package Manager:** Bun

---

## 🚀 Getting Started

### 1. Prerequisites
Make sure you have [Bun](https://bun.sh/) installed on your machine. We use Bun for blazingly fast dependency installation and script execution.

### 2. Installation
Navigate into the `dashboard` directory and install the dependencies:
```bash
cd dashboard
bun install
```

### 3. Environment Variables
Create a `.env.local` file in the root of the `dashboard` folder. You will need to add your static REST API Key from the MapmyIndia (Mappls) developer portal so the map tiles can render correctly.

```env
# Do NOT use the OAuth Client ID/Secret here! Use the REST API Key.
NEXT_PUBLIC_MAPMYINDIA_KEY=your_static_rest_api_key_here
```

### 4. Run the Development Server
Start the Next.js development server:
```bash
bun run dev
```
Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

---

## 🗺️ MapmyIndia Integration

By default, `react-leaflet` uses OpenStreetMap. We override this to use **MapmyIndia (Mappls)** to meet the hackathon criteria. 

The `TileLayer` component in our Map view uses the following endpoint structure to fetch high-resolution, localized map tiles dynamically as the user scrolls and zooms:
```text
https://tiles.mappls.com/tiles/{z}/{x}/{y}.png?access_token=YOUR_STATIC_KEY
```

---

## 📊 Data Architecture & Flow

To comply with the hackathon's architectural requirements (and to keep our demo blazing fast), this dashboard **does not rely on a live database or a live Python backend server**. 

Instead, the UI is entirely decoupled from the data engineering pipeline. It reads directly from two static JSON artifacts that were pre-compiled and sorted by the backend:

1. **`data/zone_summary.json`**: Contains the pre-sorted list of congestion zones, including Priority Scores, Action Tiers (TOW/PATROL/MONITOR), vehicle breakdown stats, and recommended patrol windows.
2. **`data/zones.geojson`**: Contains the geospatial Point data and dynamic radius sizes (`radius_m`) used to draw the circular hotspots on the map.

Because the data is pre-processed, the dashboard enjoys zero-latency loading and effortless hosting!

---

*Built with ❤️ for Gridlock 2.0*
