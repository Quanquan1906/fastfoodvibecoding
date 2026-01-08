import React, { useEffect, useState } from "react";
import DroneMap from "../../components/DroneMap";
import "./Customer.css";

// Minimal visual-only demo: no backend, no GPS.
// Change these coordinates to match your demo city.
const RESTAURANT = { lat: 37.7749, lng: -122.4194 };
const CUSTOMER = { lat: 37.7849, lng: -122.4094 };

export default function TrackingDemo() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setProgress((p) => (p >= 100 ? 100 : p + 2));
    }, 250);

    return () => clearInterval(id);
  }, []);

  return (
    <div className="page-container">
      <div className="header">
        <h1>Drone Tracking Demo</h1>
      </div>

      <div style={{ maxWidth: 900, margin: "0 auto" }}>
        <DroneMap
          startLat={RESTAURANT.lat}
          startLng={RESTAURANT.lng}
          endLat={CUSTOMER.lat}
          endLng={CUSTOMER.lng}
          progress={progress}
        />

        <div style={{ marginTop: 12 }}>
          <div>Progress: {progress}%</div>
          <button className="btn btn-secondary" onClick={() => setProgress(0)}>
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}
