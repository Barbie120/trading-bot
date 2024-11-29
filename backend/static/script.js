// Fetch and display statistics
async function fetchStats() {
    const response = await fetch('/stats');
    const stats = await response.json();

    document.getElementById('total-trades').textContent = stats.total_trades;
    document.getElementById('wins').textContent = stats.wins;
    document.getElementById('losses').textContent = stats.losses;
    document.getElementById('win-rate').textContent = stats.win_rate.toFixed(2);
}

// Fetch and display trade data
async function fetchTrades() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    let url = '/trades';

    if (startDate || endDate) {
        url += `?start_date=${startDate}&end_date=${endDate}`;
    }

    const response = await fetch(url);
    const trades = await response.json();
    const tradeHistory = document.getElementById('trade-history');

    tradeHistory.innerHTML = '';

    if (trades.length === 0) {
        tradeHistory.innerHTML = '<tr><td colspan="3">No trades found.</td></tr>';
        return;
    }

    trades.forEach(trade => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${trade.time}</td>
            <td>${trade.type}</td>
            <td>${trade.profit}</td>
        `;
        tradeHistory.appendChild(row);
    });
}

// Initial Fetch
fetchStats();
fetchTrades();
