// Main JavaScript for TP-Link HS300 Power Strip Web Controller

/**
 * Load all outlets and display them
 */
async function loadOutlets() {
    const grid = document.getElementById('outlets-grid');
    const deviceInfo = document.getElementById('device-info');
    
    // Show loading state
    grid.innerHTML = '<div class="loading-message"><div class="spinner"></div><p>Loading outlets...</p></div>';
    deviceInfo.innerHTML = '<span class="loading">Loading device information...</span>';
    
    try {
        const response = await fetch('/api/outlets');
        const data = await response.json();
        
        if (data.error) {
            grid.innerHTML = `<div class="error-message">Error: ${data.error}</div>`;
            deviceInfo.innerHTML = `<span style="color: var(--secondary-color);">Connection Error</span>`;
            return;
        }
        
        // Update device info
        deviceInfo.innerHTML = `
            <strong>Device:</strong> ${data.device_name} | 
            <strong>IP:</strong> ${data.ip_address}
        `;
        
        // Render outlets
        grid.innerHTML = '';
        const outlets = data.outlets;
        
        for (const [num, outlet] of Object.entries(outlets)) {
            const outletCard = createOutletCard(parseInt(num), outlet);
            grid.appendChild(outletCard);
        }
        
    } catch (error) {
        grid.innerHTML = `<div class="error-message">Error loading outlets: ${error.message}</div>`;
        deviceInfo.innerHTML = `<span style="color: var(--secondary-color);">Connection Error</span>`;
    }
}

/**
 * Create an outlet card element
 */
function createOutletCard(outletNum, outlet) {
    const card = document.createElement('div');
    card.className = `outlet-card ${outlet.state === 1 ? 'on' : 'off'}`;
    card.id = `outlet-${outletNum}`;
    
    const statusClass = outlet.state === 1 ? 'on' : 'off';
    const statusText = outlet.state === 1 ? 'ON' : 'OFF';
    const statusIcon = outlet.state === 1 ? '🟢' : '🔴';
    
    card.innerHTML = `
        <div class="outlet-header">
            <span class="outlet-number">#${outletNum}</span>
            <span class="outlet-status ${statusClass}">${statusIcon} ${statusText}</span>
        </div>
        <div class="outlet-name">${escapeHtml(outlet.name)}</div>
        <div class="outlet-controls">
            <button class="btn btn-on" onclick="toggleOutlet(${outletNum}, 'on')">
                <span class="icon">⚡</span> ON
            </button>
            <button class="btn btn-off" onclick="toggleOutlet(${outletNum}, 'off')">
                <span class="icon">🔌</span> OFF
            </button>
            <button class="btn btn-power" onclick="showPowerDraw(${outletNum})">
                <span class="icon">📊</span> Power
            </button>
        </div>
    `;
    
    return card;
}

/**
 * Toggle a specific outlet
 */
async function toggleOutlet(outletNum, action) {
    // Disable buttons during operation
    const buttons = document.querySelectorAll(`#outlet-${outletNum} .btn`);
    buttons.forEach(btn => btn.disabled = true);
    
    try {
        const response = await fetch(`/api/outlet/${outletNum}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: action })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Reload outlets to update status
            await loadOutlets();
            
            // Show success message briefly
            showMessage(`Outlet ${outletNum} turned ${action.toUpperCase()}`, 'success');
        } else {
            showMessage(`Error: ${data.error}`, 'error');
            // Re-enable buttons on error
            buttons.forEach(btn => btn.disabled = false);
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
        buttons.forEach(btn => btn.disabled = false);
    }
}

/**
 * Toggle all outlets
 */
async function toggleAllOutlets(action) {
    const buttons = document.querySelectorAll('.controls-bar .btn');
    buttons.forEach(btn => btn.disabled = true);
    
    try {
        const response = await fetch('/api/outlets/all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: action })
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadOutlets();
            showMessage(`All outlets turned ${action.toUpperCase()}`, 'success');
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        buttons.forEach(btn => btn.disabled = false);
    }
}

/**
 * Load power table of all outlets and display them with a sum at the bottom
 */
async function loadPowerTable() {
    const response = await fetch('/api/outlets/all/power');
    const data = await response.json();
    const powerData = data.power_data;
    console.log(powerData);
    const tableBody = document.querySelector('tbody');
    powerData.forEach(power => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${power.outlet_num}</td>
            <td>${power.power}</td>
        `;
        tableBody.appendChild(row);
    });
/**
 * Show power draw information for an outlet
 */
async function showPowerDraw(outletNum) {
    const modal = document.getElementById('power-modal');
    const modalTitle = document.getElementById('power-modal-title');
    const modalBody = document.getElementById('power-modal-body');
    
    modal.style.display = 'block';
    modalTitle.textContent = `Power Draw - Outlet ${outletNum}`;
    modalBody.innerHTML = '<div class="loading-message"><div class="spinner"></div><p>Loading power data...</p></div>';
    
    try {
        const response = await fetch(`/api/outlet/${outletNum}/power`);
        const data = await response.json();
        
        if (data.success) {
            const powerData = data.power_data;
            modalTitle.textContent = `Power Draw - ${data.outlet_name}`;
            
            let html = '<div class="power-data">';
            
            if (powerData.voltage !== undefined) {
                html += `
                    <div class="power-data-item">
                        <span class="power-data-label">Voltage:</span>
                        <span class="power-data-value">${powerData.voltage.toFixed(2)} V</span>
                    </div>
                `;
            }
            
            if (powerData.current !== undefined) {
                html += `
                    <div class="power-data-item">
                        <span class="power-data-label">Current:</span>
                        <span class="power-data-value">${powerData.current.toFixed(3)} A</span>
                    </div>
                `;
            }
            
            if (powerData.power !== undefined) {
                html += `
                    <div class="power-data-item">
                        <span class="power-data-label">Power:</span>
                        <span class="power-data-value">${powerData.power.toFixed(2)} W</span>
                    </div>
                `;
            }
            
            if (powerData.total !== undefined) {
                html += `
                    <div class="power-data-item">
                        <span class="power-data-label">Total Energy:</span>
                        <span class="power-data-value">${powerData.total.toFixed(3)} kWh</span>
                    </div>
                `;
            }
            
            if (Object.keys(powerData).length === 0) {
                html += '<div class="error-message">No power data available for this outlet.</div>';
            }
            
            html += '</div>';
            modalBody.innerHTML = html;
        } else {
            modalBody.innerHTML = `<div class="error-message">Error: ${data.error}</div>`;
        }
    } catch (error) {
        modalBody.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
}

/**
 * Show a temporary message
 */
function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = type === 'success' ? 'success-message' : 'error-message';
    messageDiv.textContent = message;
    messageDiv.style.position = 'fixed';
    messageDiv.style.top = '20px';
    messageDiv.style.right = '20px';
    messageDiv.style.zIndex = '2000';
    messageDiv.style.minWidth = '300px';
    messageDiv.style.maxWidth = '500px';
    
    document.body.appendChild(messageDiv);
    
    // Remove after 3 seconds
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        messageDiv.style.transition = 'opacity 0.3s';
        setTimeout(() => messageDiv.remove(), 300);
    }, 3000);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

