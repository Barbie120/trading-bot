import React, { useEffect, useState } from "react";

const App = () => {
  const [trades, setTrades] = useState([]);
  const [stats, setStats] = useState({});

  // Fetch trades and stats on component mount
  useEffect(() => {
    fetch("http://localhost:5000/api/trades")
      .then((res) => res.json())
      .then((data) => setTrades(data))
      .catch((err) => console.error("Error fetching trades:", err));

    fetch("http://localhost:5000/api/stats")
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error("Error fetching stats:", err));
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>Trading Dashboard</h1>
      <h2>Statistics</h2>
      <p>Win Rate: {stats.winRate || "Loading..."}%</p>
      <p>Total Trades: {stats.totalTrades || "Loading..."}</p>
      <p>Profit: ${stats.profit || "Loading..."}</p>

      <h2>Trades</h2>
      <table border="1" style={{ width: "100%", textAlign: "left" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Symbol</th>
            <th>Type</th>
            <th>Price</th>
            <th>Amount</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {trades.length > 0 ? (
            trades.map((trade) => (
              <tr key={trade.id}>
                <td>{trade.id}</td>
                <td>{trade.symbol}</td>
                <td>{trade.type}</td>
                <td>{trade.price}</td>
                <td>{trade.amount}</td>
                <td>{trade.timestamp}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6">Loading trades...</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default App;
