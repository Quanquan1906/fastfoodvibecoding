import React, { useMemo } from "react";
import { MapContainer, TileLayer, Marker, Polyline } from "react-leaflet";
import L from "leaflet";

import "leaflet/dist/leaflet.css";

// Fix default marker icons in bundlers like CRA/Vite
// (Leaflet expects these assets to be available at runtime)
// https://github.com/PaulLeCam/react-leaflet/issues/453
// Safe to run multiple times.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function clamp01(x) {
  return Math.max(0, Math.min(1, x));
}

function DroneMap({ startLat, startLng, endLat, endLng, progress }) {
  const sLat = Number(startLat);
  const sLng = Number(startLng);
  const rawELat = Number(endLat);
  const rawELng = Number(endLng);

  const isValid =
    Number.isFinite(sLat) &&
    Number.isFinite(sLng) &&
    Number.isFinite(rawELat) &&
    Number.isFinite(rawELng);

  // Demo safeguard: if start/end are identical, nudge the end point a bit so
  // the polyline and movement are visible.
  const samePoint = sLat === rawELat && sLng === rawELng;
  const eLat = samePoint ? sLat + 0.01 : rawELat;
  const eLng = samePoint ? sLng + 0.01 : rawELng;

  // Required: t = progress / 100
  const t = clamp01(Number(progress) / 100);

  // Required linear interpolation (guarantees 100% => exactly at destination)
  const droneLat = lerp(sLat, eLat, t);
  const droneLng = lerp(sLng, eLng, t);
  const dronePos = [droneLat, droneLng];

  const polylinePositions = useMemo(() => {
    return [
      [sLat, sLng],
      [eLat, eLng],
    ];
  }, [sLat, sLng, eLat, eLng]);

  const bounds = polylinePositions;

  if (!isValid) {
    return null;
  }

  return (
    <div style={{ height: 320, width: "100%" }}>
      <MapContainer
        style={{ height: "100%", width: "100%" }}
        bounds={bounds}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <Polyline positions={polylinePositions} />
        <Marker position={[sLat, sLng]} />
        <Marker position={[eLat, eLng]} />
        <Marker position={dronePos} />
      </MapContainer>
    </div>
  );
}

export default DroneMap;
