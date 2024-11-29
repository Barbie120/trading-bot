// Fetch statistics
fetch('/api/stats')
  .then(response => response.json())
  .then(data => {
    document.getElementById('total-trades').innerText = data.totalTrades || '0';
    document.getElementById('wins').innerText = data.wins || '0';
    document.getElementById('losses').innerText = data.losses || '0';
    document.getElementById('win-rate').innerText = data.winRate || '0%';
  })
  .catch(error => console.error('Error fetching stats:', error));

// Fetch trades
fetch('/api/trades')
  .then(response => response.json())
  .then(data => {
    const tradeHistory = document.getElementById('trade-history');
    data.forEach(trade => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${trade.time}</td>
        <td>${trade.type}</td>
        <td>${trade.profit}</td>
      `;
      tradeHistory.appendChild(row);
    });
  })
  .catch(error => console.error('Error fetching trades:', error));
