import { useState, useEffect } from "react";
import { getStats } from "./api.ts";

type Stats = {
  total_current_deals: number;
  vectorized_deals: number;
  priced_deals: number;
  price_new_known_deals: number;
  deals_with_eta: number;
  deals_above_predicted: number;
  valid_deals: number;
};

export const StatsView = () => {
  const [stats, setStats] = useState<Stats>();

  useEffect(() => {
    const fetchStats = async () => {
      const response: Stats[] = await getStats();
      setStats(response[0]);
    };
    fetchStats();
  }, []);

  if (!stats) {
    return <div>Loading...</div>;
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        padding: "1rem",
      }}
    >
      <div
        style={{
          width: "90vw",
          backgroundColor: "var(--accent)",
          padding: "1rem",
        }}
      >
        <p>Current deals: {stats.total_current_deals}</p>
      </div>
      <div
        style={{
          width:
            (stats.vectorized_deals / (stats.total_current_deals + 1)) * 90 +
            "vw",
          backgroundColor: "var(--accent)",
          padding: "1rem",
        }}
      >
        <p>of them vectorized: {stats.vectorized_deals}</p>
      </div>
      <div
        style={{
          width:
            (stats.price_new_known_deals / (stats.total_current_deals + 1)) *
              90 +
            "vw",
          backgroundColor: "var(--accent)",
          padding: "1rem",
        }}
      >
        <p>of them known price of new: {stats.price_new_known_deals}</p>
      </div>
      <div
        style={{
          width:
            (stats.priced_deals / (stats.total_current_deals + 1)) * 90 + "vw",
          backgroundColor: "var(--accent)",
          padding: "1rem",
        }}
      >
        <p>of them priced: {stats.priced_deals}</p>
      </div>
      <div
        style={{
          width:
            (stats.deals_above_predicted / (stats.total_current_deals + 1)) *
              90 +
            "vw",
          backgroundColor: "var(--accent)",
          padding: "1rem",
        }}
      >
        <p>of them above predicted: {stats.deals_above_predicted}</p>
      </div>
      <div
        style={{
          width:
            (stats.valid_deals / (stats.total_current_deals + 1)) * 90 + "vw",
          backgroundColor: "var(--accent)",
          padding: "1rem",
        }}
      >
        <p>of them valid and liquid: {stats.valid_deals}</p>
      </div>
      <div
        style={{
          width:
            (stats.deals_with_eta / (stats.total_current_deals + 1)) * 90 +
            "vw",
          backgroundColor: "var(--accent)",
          padding: "1rem",
        }}
      >
        <p>of them with eta: {stats.deals_with_eta}</p>
      </div>
    </div>
  );
};
