/**
 * Power Strip Manager
 * Handles multiple power strip configuration and selection
 */

(function() {
    'use strict';
    
    const STORAGE_KEY = 'kasa_hs300_selected_power_strip_id';
    let powerStrips = [];
    let activePowerStripId = null;
    
    /**
     * Get selected power strip ID from localStorage or return null
     */
    function getSelectedPowerStripId() {
        return localStorage.getItem(STORAGE_KEY);
    }
    
    /**
     * Set selected power strip ID in localStorage
     */
    function setSelectedPowerStripId(powerStripId) {
        if (powerStripId) {
            localStorage.setItem(STORAGE_KEY, powerStripId);
        } else {
            localStorage.removeItem(STORAGE_KEY);
        }
    }
    
    /**
     * Load power strips from API
     */
    async function loadPowerStrips() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.success) {
                powerStrips = data.power_strips || [];
                activePowerStripId = data.active_power_strip_id || (powerStrips.length > 0 ? powerStrips[0].id : null);
                
                // Use selected from localStorage or fall back to active
                const selectedId = getSelectedPowerStripId() || activePowerStripId;
                if (selectedId && powerStrips.find(ps => ps.id === selectedId)) {
                    activePowerStripId = selectedId;
                }
                
                return { success: true, powerStrips, activePowerStripId };
            }
            return { success: false, error: 'Failed to load power strips' };
        } catch (error) {
            console.error('Error loading power strips:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Populate power strip selector dropdown
     */
    function populateSelector() {
        const selector = document.getElementById('power-strip-selector');
        if (!selector) return;
        
        selector.innerHTML = '';
        
        if (powerStrips.length === 0) {
            selector.innerHTML = '<option value="">No power strips configured</option>';
            return;
        }
        
        powerStrips.forEach(ps => {
            const option = document.createElement('option');
            option.value = ps.id;
            option.textContent = `${ps.name} (${ps.ip_address})`;
            if (ps.id === activePowerStripId) {
                option.selected = true;
            }
            selector.appendChild(option);
        });
    }
    
    /**
     * Set active power strip
     */
    async function setActivePowerStrip(powerStripId) {
        try {
            const response = await fetch('/api/config/active', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ power_strip_id: powerStripId })
            });
            
            const data = await response.json();
            if (data.success) {
                activePowerStripId = powerStripId;
                setSelectedPowerStripId(powerStripId);
                populateSelector();
                return { success: true };
            }
            return { success: false, error: data.error || 'Failed to set active power strip' };
        } catch (error) {
            console.error('Error setting active power strip:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Get current active power strip ID
     */
    function getActivePowerStripId() {
        return activePowerStripId;
    }
    
    /**
     * Initialize power strip manager
     */
    async function init() {
        const result = await loadPowerStrips();
        if (result.success) {
            populateSelector();
            
            // Add change handler to selector
            const selector = document.getElementById('power-strip-selector');
            if (selector) {
                selector.addEventListener('change', async function(e) {
                    const selectedId = e.target.value;
                    if (selectedId) {
                        await setActivePowerStrip(selectedId);
                        // Trigger reload of outlets if loadOutlets function exists
                        if (typeof loadOutlets === 'function') {
                            await loadOutlets();
                        }
                        // Trigger reload of power table if loadPowerTable function exists
                        if (typeof loadPowerTable === 'function') {
                            await loadPowerTable();
                        }
                    }
                });
            }
        }
        return result;
    }
    
    // Export to window
    window.PowerStripManager = {
        init,
        loadPowerStrips,
        getActivePowerStripId,
        setActivePowerStrip,
        getPowerStrips: () => powerStrips
    };
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

