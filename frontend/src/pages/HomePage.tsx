import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Skeleton from "../components/Skeleton";
import { fetchHomeKPIsApi, type HomeKPITile } from "../api/home";

export default function HomePage(): JSX.Element {
  const [tiles, setTiles] = useState<HomeKPITile[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchHomeKPIsApi()
      .then((res) => {
        if (!cancelled) setTiles(res.tiles);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="home-page">
      <h1>Welcome</h1>

      {error && <div role="alert">Error: {error}</div>}

      {tiles === null && <Skeleton lines={4} />}

      {tiles !== null && tiles.length === 0 && (
        <EmptyState
          title="No metrics yet"
          description="Your KPI dashboard will populate as you begin using the ERP modules."
        />
      )}

      {tiles !== null && tiles.length > 0 && (
        <div className="kpi-grid">
          {tiles.map((tile) => (
            <div key={tile.label} className="kpi-tile">
              <div className="kpi-label">{tile.label}</div>
              <div className="kpi-value">{tile.value}</div>
              {tile.detail && <div className="kpi-detail">{tile.detail}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
