'use client';

// ---------------------------------------------------------------------------
// CurbOps — MapSearch
// 100% dataset-driven search with autocomplete over Bengaluru enforcement zones.
// Matches zone_name, display_name, cluster_name, junction_name, station_name, police_station.
// ---------------------------------------------------------------------------

import { useEffect, useRef, useState } from 'react';
import type { Zone } from '@/lib/dashboard/types';
import { getJunctionDisplayName } from '@/lib/dashboard/tiers';

export interface PlaceResult {
  placeId: number;
  lat: number;
  lon: number;
  label: string;        // primary name
  detail: string;       // secondary line (type / district)
  zone: Zone;           // reference to full zone object
}

interface MapSearchProps {
  zones: Zone[];
  onSelect: (place: PlaceResult) => void;
  onOpenChange?: (open: boolean) => void;
}

function highlightText(text: string, query: string) {
  if (!query.trim()) return <span>{text}</span>;
  const regex = new RegExp(`(${query.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi');
  const parts = text.split(regex);
  return (
    <span>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark key={i} className="bg-cyan-500/20 text-[#22d3ee] font-semibold px-0.5 rounded">
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </span>
  );
}

export default function MapSearch({ zones, onSelect, onOpenChange }: MapSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PlaceResult[]>([]);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  const boxRef = useRef<HTMLDivElement>(null);

  // Load recent searches
  useEffect(() => {
    const saved = localStorage.getItem('curbops_recent_searches');
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch {}
    }
  }, []);

  // Save to recent searches
  const saveRecentSearch = (q: string) => {
    if (!q.trim() || q.trim().length < 2) return;
    const cleanQ = q.trim();
    const updated = [cleanQ, ...recentSearches.filter((x) => x !== cleanQ)].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem('curbops_recent_searches', JSON.stringify(updated));
  };

  // Perform dataset search
  useEffect(() => {
    const q = query.trim().toLowerCase();
    if (q.length < 2) {
      setResults([]);
      return;
    }

    // Filter and score zones
    const scored = zones
      .map((z) => {
        const jName = getJunctionDisplayName(z).toLowerCase();
        const station = z.police_station.toLowerCase();
        const zId = String(z.zone_id);
        const zName = `zone ${zId}`;
        const zHash = `zone #${zId}`;

        let score = 0;

        if (zId === q || zHash === q || zName === q) {
          score = 100;
        } else if (jName === q) {
          score = 95;
        } else if (station === q || `${station} ps` === q || `${station} police station` === q) {
          score = 90;
        } else if (jName.startsWith(q)) {
          score = 80;
        } else if (station.startsWith(q)) {
          score = 70;
        } else if (zName.startsWith(q) || zHash.startsWith(q)) {
          score = 65;
        } else if (jName.includes(q)) {
          score = 50;
        } else if (station.includes(q)) {
          score = 40;
        } else if (zId.includes(q)) {
          score = 30;
        }

        // Add CBM ranking factor to break ties
        if (score > 0) {
          score += (z.zone_CBM_sum || 0) / 1000000;
        }

        return { z, score };
      })
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 8)
      .map((item) => {
        const z = item.z;
        return {
          placeId: z.zone_id,
          lat: z.centroid_lat,
          lon: z.centroid_lon,
          label: getJunctionDisplayName(z),
          detail: `Zone #${z.zone_id} · ${z.police_station} PS · CBM: ${Math.round(z.zone_CBM_sum).toLocaleString('en-IN')}`,
          zone: z,
        };
      });

    setResults(scored);
    setActiveIndex(scored.length > 0 ? 0 : -1);
  }, [query, zones]);

  // Close on click outside
  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  const choose = (place: PlaceResult) => {
    onSelect(place);
    setQuery(place.label);
    saveRecentSearch(place.label);
    setOpen(false);
    setResults([]);
    setActiveIndex(-1);
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!open) {
      if (e.key === 'ArrowDown') setOpen(true);
      return;
    }
    if (results.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((i) => (i + 1) % results.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) => (i - 1 + results.length) % results.length);
    } else if (e.key === 'Enter') {
      if (activeIndex >= 0 && results[activeIndex]) {
        e.preventDefault();
        choose(results[activeIndex]);
      }
    } else if (e.key === 'Escape') {
      setOpen(false);
    }
  };

  const showDropdown = open && (query.trim().length >= 2 || (query.trim().length === 0 && recentSearches.length > 0));

  useEffect(() => {
    onOpenChange?.(showDropdown);
  }, [showDropdown, onOpenChange]);

  return (
    <div ref={boxRef} className="map-search-wrap">
      <div className="map-search-input-row">
        <svg
          className="map-search-icon"
          viewBox="0 0 16 16"
          fill="none"
          aria-hidden
        >
          <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.4" />
          <path
            d="M11 11 L14 14"
            stroke="currentColor"
            strokeWidth="1.4"
            strokeLinecap="round"
          />
        </svg>
        <input
          className="map-search-input font-mono"
          type="text"
          autoComplete="off"
          spellCheck={false}
          placeholder="Search zone, junction or station..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
            setActiveIndex(-1);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={onKeyDown}
          aria-label="Search zones or police stations"
          aria-expanded={showDropdown}
          aria-autocomplete="list"
          role="combobox"
        />
        {query && (
          <button
            type="button"
            className="map-search-clear"
            onClick={() => {
              setQuery('');
              setResults([]);
              setActiveIndex(-1);
              setOpen(false);
            }}
            title="Clear search"
            aria-label="Clear search"
          >
            <svg viewBox="0 0 12 12" width="12" height="12" fill="none">
              <path
                d="M3 3 L9 9 M9 3 L3 9"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </svg>
          </button>
        )}
      </div>

      {showDropdown && (
        <ul role="listbox" className="map-search-list font-mono">
          {/* Recent Searches state */}
          {query.trim().length === 0 && recentSearches.length > 0 && (
            <>
              <li className="px-3 py-1.5 text-[9px] uppercase tracking-wider text-slate-500 font-semibold border-b border-white/5">
                Recent Searches
              </li>
              {recentSearches.map((s, idx) => (
                <li
                  key={`recent-${idx}`}
                  role="option"
                  className="map-search-item text-slate-300 hover:text-[#22d3ee] text-[11px] px-3 py-2 cursor-pointer flex items-center gap-2"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    setQuery(s);
                  }}
                >
                  <svg viewBox="0 0 12 12" width="11" height="11" fill="none" className="text-slate-500">
                    <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1" />
                    <path d="M6 3 V6 H8" stroke="currentColor" strokeWidth="1" />
                  </svg>
                  {s}
                </li>
              ))}
            </>
          )}

          {/* Regular Results */}
          {query.trim().length >= 2 && results.length === 0 && (
            <li className="map-search-empty text-slate-500 text-[11px] px-3 py-4 text-center">
              No zones match &ldquo;{query}&rdquo;.
            </li>
          )}

          {query.trim().length >= 2 && results.map((r, i) => (
            <li
              key={r.placeId}
              role="option"
              aria-selected={i === activeIndex}
              className={`map-search-item ${i === activeIndex ? 'active' : ''}`}
              onMouseDown={(e) => {
                e.preventDefault();
                choose(r);
              }}
              onMouseEnter={() => setActiveIndex(i)}
            >
              <span className="map-search-pin text-[#22d3ee]" aria-hidden>
                <svg viewBox="0 0 12 12" width="11" height="11" fill="none">
                  <path
                    d="M6 1 C3.8 1 2 2.7 2 4.8 C2 7.6 6 11 6 11 C6 11 10 7.6 10 4.8 C10 2.7 8.2 1 6 1 Z"
                    stroke="currentColor"
                    strokeWidth="1.2"
                    fill="none"
                  />
                  <circle cx="6" cy="4.8" r="1.3" fill="currentColor" />
                </svg>
              </span>
              <span className="map-search-text">
                <span className="map-search-label text-slate-100">
                  {highlightText(r.label, query)}
                </span>
                {r.detail && (
                  <span className="map-search-detail text-slate-400 text-[10px] mt-0.5">
                    {highlightText(r.detail, query)}
                  </span>
                )}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
