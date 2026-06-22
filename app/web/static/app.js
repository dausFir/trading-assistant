// WebSocket connection
const socket = new WebSocket(`ws://${window.location.host}/ws`);

// Current market tab
let currentMarket = 'crypto';

// Market data storage
const marketData = {
    crypto: {},
    ihsg: {},
    us: {}
};

// Socket event handlers
socket.onopen = () => {
    document.getElementById('connection-status').textContent = 'Connected';
    document.getElementById('connection-status').style.color = 'var(--green)';
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'candle') {
        const market = data.market || 'crypto';
        updatePrice(market, data.symbol, data.data.close);
        document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
    }
    
    if (data.type === 'signal') {
        addSignal(data.signal);
    }
};

socket.onclose = () => {
    document.getElementById('connection-status').textContent = 'Disconnected';
    document.getElementById('connection-status').style.color = 'var(--red)';
    
    // Attempt reconnect after 3 seconds
    setTimeout(() => {
        location.reload();
    }, 3000);
};

// Update price display
function updatePrice(market, symbol, price) {
    marketData[market][symbol] = price;
    
    // Only update if viewing this market
    if (market === currentMarket) {
        const grid = document.getElementById('price-grid');
        let card = document.getElementById(`price-${symbol}`);
        
        if (!card) {
            card = document.createElement('div');
            card.className = 'card';
            card.id = `price-${symbol}`;
            grid.appendChild(card);
        }
        
        const formattedPrice = price >= 1 ? 
            price.toLocaleString('en-US', {style: 'currency', currency: 'USD'}) :
            price.toFixed(6);
        
        card.innerHTML = `<h3>${symbol}</h3><p class="price">${formattedPrice}</p>`;
    }
}

// Add signal to list
function addSignal(signal) {
    const container = document.getElementById('signals-container');
    
    // Remove empty state if present
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const signalEl = document.createElement('div');
    signalEl.className = `signal ${signal.setup_type}`;
    signalEl.innerHTML = `
        <strong>${signal.symbol}</strong> ${signal.setup_type}
        <br>Price: ${signal.price}
        <br>Score: ${signal.score || 'N/A'}
    `;
    
    // Add to top
    container.insertBefore(signalEl, container.firstChild);
    
    // Keep only last 10 signals
    while (container.children.length > 10) {
        container.removeChild(container.lastChild);
    }
}

// Market tab switching
const tabs = document.querySelectorAll('.tab');
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Update active tab
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Update current market
        currentMarket = tab.dataset.market;
        
        // Refresh price display
        refreshPrices();
    });
});

function refreshPrices() {
    const grid = document.getElementById('price-grid');
    grid.innerHTML = '';
    
    const data = marketData[currentMarket];
    for (const [symbol, price] of Object.entries(data)) {
        updatePrice(currentMarket, symbol, price);
    }
    
    if (Object.keys(data).length === 0) {
        grid.innerHTML = '<div class="empty-state">Waiting for price data...</div>';
    }
}

// Uptime timer
let seconds = 0;
setInterval(() => {
    seconds++;
    const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
    const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    document.getElementById('uptime').textContent = `${h}:${m}:${s}`;
}, 1000);
