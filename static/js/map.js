/**
 * Google Maps API & Spatial Mapping Engine
 * Antigravity Dark Cosmic Map Theme & Interactive Pinpoint Controls
 */

let googleMap = null;
let currentInfoWindow = null;
let markers = [];
let buildingMarkers = [];

// Antigravity Dark Cyberpunk Theme for Google Maps
const ANTIGRAVITY_MAP_STYLES = [
  { "elementType": "geometry", "stylers": [{ "color": "#080d1a" }] },
  { "elementType": "labels.text.fill", "stylers": [{ "color": "#94a3b8" }] },
  { "elementType": "labels.text.stroke", "stylers": [{ "color": "#060912" }, { "weight": 2 }] },
  {
    "featureType": "administrative",
    "elementType": "geometry",
    "stylers": [{ "color": "#1e293b" }]
  },
  {
    "featureType": "administrative.country",
    "elementType": "labels.text.fill",
    "stylers": [{ "color": "#38bdf8" }]
  },
  {
    "featureType": "poi",
    "elementType": "geometry",
    "stylers": [{ "color": "#0f172a" }]
  },
  {
    "featureType": "poi",
    "elementType": "labels.text.fill",
    "stylers": [{ "color": "#64748b" }]
  },
  {
    "featureType": "poi.park",
    "elementType": "geometry",
    "stylers": [{ "color": "#0a192f" }]
  },
  {
    "featureType": "poi.school",
    "elementType": "geometry",
    "stylers": [{ "color": "#111c38" }]
  },
  {
    "featureType": "road",
    "elementType": "geometry",
    "stylers": [{ "color": "#16233b" }]
  },
  {
    "featureType": "road",
    "elementType": "geometry.stroke",
    "stylers": [{ "color": "#0b1220" }]
  },
  {
    "featureType": "road.highway",
    "elementType": "geometry",
    "stylers": [{ "color": "#1e3a8a" }]
  },
  {
    "featureType": "road.highway",
    "elementType": "geometry.stroke",
    "stylers": [{ "color": "#0284c7" }]
  },
  {
    "featureType": "transit",
    "elementType": "geometry",
    "stylers": [{ "color": "#0f172a" }]
  },
  {
    "featureType": "water",
    "elementType": "geometry",
    "stylers": [{ "color": "#050b18" }]
  },
  {
    "featureType": "water",
    "elementType": "labels.text.fill",
    "stylers": [{ "color": "#00f2fe" }]
  }
];

// SVG Pin Generators for Google Maps
function getCustomPin(type, label = '') {
  let color = '#00f2fe';
  let glowColor = 'rgba(0, 242, 254, 0.6)';
  if (type === 'LOST') {
    color = '#ff3366';
    glowColor = 'rgba(255, 51, 102, 0.6)';
  } else if (type === 'FOUND') {
    color = '#00f5a0';
    glowColor = 'rgba(0, 245, 160, 0.6)';
  } else if (type === 'BUILDING') {
    color = '#a855f7';
    glowColor = 'rgba(168, 85, 247, 0.6)';
  }

  const svg = `
  <svg width="36" height="46" viewBox="0 0 36 46" fill="none" xmlns="http://www.w3.org/2000/svg">
    <filter id="glow" x="0" y="0" width="36" height="46" filterUnits="userSpaceOnUse">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <path d="M18 42C18 42 32 26 32 16C32 8.26801 25.732 2 18 2C10.268 2 4 8.26801 4 16C4 26 18 42 18 42Z" fill="#090e1a" stroke="${color}" stroke-width="2.5" filter="url(#glow)"/>
    <circle cx="18" cy="16" r="6" fill="${color}"/>
  </svg>`;

  return {
    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg),
    scaledSize: new google.maps.Size(36, 46),
    anchor: new google.maps.Point(18, 44)
  };
}

// Global Callback invoked when Google Maps JS library finishes loading
function initGoogleMap() {
  const mapElement = document.getElementById('google-campus-map');
  if (!mapElement) return;

  const defaultCenter = window.CAMPUS_MAP_CENTER || { lat: 12.971598, lng: 77.594566 };

  // Create Google Map
  googleMap = new google.maps.Map(mapElement, {
    center: defaultCenter,
    zoom: 16.2,
    styles: ANTIGRAVITY_MAP_STYLES,
    mapTypeControl: true,
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_RIGHT
    },
    streetViewControl: false,
    fullscreenControl: true,
    zoomControl: true,
    backgroundColor: '#06080e'
  });

  currentInfoWindow = new google.maps.InfoWindow();

  // Load building nodes and item pins
  loadMapData();
}

// Fetch marker data from Flask backend API
function loadMapData() {
  fetch('/api/map-markers')
    .then(res => res.json())
    .then(data => {
      // 1. Plot Campus Buildings
      if (data.buildings && data.buildings.length > 0) {
        data.buildings.forEach(b => {
          const marker = new google.maps.Marker({
            position: { lat: b.lat, lng: b.lng },
            map: googleMap,
            title: b.name,
            icon: getCustomPin('BUILDING')
          });

          marker.addListener('click', () => {
            const content = `
              <div style="background: #0f1629; color: #fff; padding: 12px; border-radius: 10px; border: 1px solid #a855f7; min-width: 200px; font-family: sans-serif;">
                <div style="font-size: 11px; color: #c084fc; font-weight: bold; text-transform: uppercase;">Campus Building</div>
                <div style="font-size: 15px; font-weight: bold; margin-top: 2px;">${escapeHtml(b.name)}</div>
                <div style="font-size: 12px; color: #94a3b8; margin: 6px 0 10px;">${escapeHtml(b.desc)}</div>
                <a href="/map?zone=${encodeURIComponent(b.name)}" style="display: inline-block; background: #7f00ff; color: #fff; font-size: 12px; padding: 5px 12px; border-radius: 20px; text-decoration: none; font-weight: bold;">Filter Items Here &rarr;</a>
              </div>
            `;
            currentInfoWindow.setContent(content);
            currentInfoWindow.open(googleMap, marker);
          });

          buildingMarkers.push({ name: b.name, marker: marker, coords: { lat: b.lat, lng: b.lng } });
        });
      }

      // 2. Plot Active Items
      if (data.items && data.items.length > 0) {
        data.items.forEach(item => {
          if (!item.latitude || !item.longitude || (item.latitude === 0 && item.longitude === 0)) return;

          // Add slight jitter if multiple items at same point so they don't completely overlap
          const jitterLat = item.latitude + (Math.random() - 0.5) * 0.00015;
          const jitterLng = item.longitude + (Math.random() - 0.5) * 0.00015;

          const marker = new google.maps.Marker({
            position: { lat: jitterLat, lng: jitterLng },
            map: googleMap,
            title: item.title,
            icon: getCustomPin(item.type)
          });

          marker.addListener('click', () => {
            const statusClass = item.status === 'RETURNED' ? '#00f2fe' : (item.type === 'LOST' ? '#ff3366' : '#00f5a0');
            const content = `
              <div style="background: #0d1426; color: #fff; padding: 12px; border-radius: 12px; border: 1px solid ${statusClass}; min-width: 220px; font-family: sans-serif; box-shadow: 0 10px 25px rgba(0,0,0,0.8);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                  <span style="font-size: 10px; font-weight: bold; color: ${statusClass}; text-transform: uppercase;">${escapeHtml(item.type)} • ${escapeHtml(item.category)}</span>
                  <span style="font-size: 10px; color: #94a3b8;">${escapeHtml(item.item_date)}</span>
                </div>
                <div style="font-size: 14px; font-weight: bold; color: #fff; margin-bottom: 6px;">${escapeHtml(item.title)}</div>
                <div style="font-size: 11px; color: #94a3b8; margin-bottom: 10px;">📍 ${escapeHtml(item.location)}</div>
                <a href="/item/${item.id}" style="display: block; text-align: center; background: #00f2fe; color: #04101e; font-size: 12px; font-weight: bold; padding: 6px 12px; border-radius: 20px; text-decoration: none;">View Item & Claim &rarr;</a>
              </div>
            `;
            currentInfoWindow.setContent(content);
            currentInfoWindow.open(googleMap, marker);
          });

          markers.push(marker);
        });
      }
    })
    .catch(err => console.error("Error loading map markers:", err));
}

// Pan Google Map to a specific campus location
function panToLocation(locationName) {
  if (!googleMap) return;
  const target = buildingMarkers.find(b => b.name === locationName);
  if (target) {
    googleMap.panTo(target.coords);
    googleMap.setZoom(17.5);
    google.maps.event.trigger(target.marker, 'click');
  }
}

// Global Google Maps Auth Failure handler
window.gm_authFailure = function() {
  const mapElement = document.getElementById('google-campus-map');
  const alertBox = document.getElementById('map-api-key-alert');
  if (alertBox) alertBox.style.display = 'block';

  if (mapElement) {
    mapElement.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 2rem; text-align: center; background: #090e1a; color: #fff;">
        <div style="width: 56px; height: 56px; border-radius: 50%; background: rgba(0, 242, 254, 0.1); border: 1px solid #00f2fe; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; color: #00f2fe;">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        </div>
        <h3 style="font-size: 1.25rem; margin-bottom: 0.5rem;">Google Maps API Key Required</h3>
        <p style="color: #94a3b8; max-width: 460px; font-size: 0.875rem; margin-bottom: 1.25rem;">
          Google Maps API requires a valid key for live maps rendering. You can paste your Google Maps API key below or switch to the Campus Blueprint view!
        </p>
        <div style="display: flex; gap: 0.75rem;">
          <button class="ag-btn ag-btn-primary ag-btn-sm" onclick="showApiKeyPrompt()">Enter Google Maps Key</button>
          <button class="ag-btn ag-btn-glass ag-btn-sm" onclick="switchMapMode('blueprint')">Switch to Blueprint View</button>
        </div>
      </div>
    `;
  }
};

// Prompt user to save/update Google Maps API Key
function showApiKeyPrompt() {
  const key = prompt("Enter your Google Maps JavaScript API Key:\n(You can obtain one at https://console.cloud.google.com/google/maps-apis)");
  if (key && key.trim()) {
    fetch('/api/set-maps-key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key.trim() })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("Google Maps API Key saved! Reloading map...");
        window.location.reload();
      }
    });
  }
}

// Utility: HTML escape
function escapeHtml(text) {
  if (!text) return '';
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.toString().replace(/[&<>"']/g, m => map[m]);
}
