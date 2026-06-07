import { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import { getOffsetCoordinates, MAHARASHTRA_GEO } from '../utils/geoData';

// Fix Leaflet's default icon path issues with Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function HeatmapLayer({ data }) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;
    
    // Prepare heat points [lat, lng, intensity]
    const heatPoints = data.map(pt => [pt.lat, pt.lng, 1]); // default intensity 1
    
    const heatLayer = L.heatLayer(heatPoints, {
      radius: 25,
      blur: 15,
      maxZoom: 10,
      max: 2,
      gradient: { 0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red' }
    }).addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [map, data]);

  return null;
}

function FitBounds({ markers, selectedCity }) {
  const map = useMap();

  useEffect(() => {
    if (selectedCity !== 'All' && MAHARASHTRA_GEO[selectedCity]) {
      const [lat, lng] = MAHARASHTRA_GEO[selectedCity];
      map.flyTo([lat, lng], 12, { animate: true, duration: 1.5 });
    } else {
      map.flyTo([19.0760, 75.8777], 6, { animate: true, duration: 1.5 }); // Central Maharashtra approx
    }
  }, [selectedCity, map]);

  return null;
}

export default function HeatMap({ institutes, selectedCity }) {
  // Memoize coordinates mapping to prevent infinite loops
  const mapData = useMemo(() => {
    return institutes.map(inst => {
      const [lat, lng] = getOffsetCoordinates(inst.city);
      return { ...inst, lat, lng };
    });
  }, [institutes]);

  return (
    <div className="w-full h-full min-h-[400px] bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden relative">
      <MapContainer 
        center={[19.0760, 75.8777]} 
        zoom={6} 
        style={{ height: '100%', width: '100%', zIndex: 0 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
        <HeatmapLayer data={mapData} />
        <FitBounds markers={mapData} selectedCity={selectedCity} />

        {mapData.map(inst => (
          <Marker key={inst.id} position={[inst.lat, inst.lng]}>
            <Popup>
              <div className="text-sm">
                <p className="font-bold mb-1">{inst.name}</p>
                <p className="text-gray-600 text-xs mb-1">{inst.category} • {inst.city}</p>
                {inst.phone && <p className="text-blue-600 text-xs mb-1">{inst.phone}</p>}
                <a href={inst.website || inst.source_url} target="_blank" rel="noreferrer" className="text-xs text-blue-500 hover:underline">
                  Visit site
                </a>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
