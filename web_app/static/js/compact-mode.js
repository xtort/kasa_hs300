/**
 * Compact Mode State Management
 * Provides site-wide compact mode state using localStorage
 */

(function() {
    'use strict';
    
    const COMPACT_MODE_KEY = 'kasa_hs300_compact_mode';
    
    /**
     * Check if compact mode is enabled
     * Checks localStorage first, then URL parameters
     */
    function isCompactMode() {
        // Check localStorage first
        const stored = localStorage.getItem(COMPACT_MODE_KEY);
        if (stored !== null) {
            return stored === 'true';
        }
        
        // Fall back to URL parameters
        const url = new URL(window.location.href);
        const params = url.searchParams;
        return params.get('compact') === 'true' ||
               params.get('compact-mode') === 'true' ||
               params.get('pi') === 'true';
    }
    
    /**
     * Set compact mode state
     */
    function setCompactMode(enabled) {
        localStorage.setItem(COMPACT_MODE_KEY, enabled ? 'true' : 'false');
        applyCompactMode(enabled);
    }
    
    /**
     * Toggle compact mode
     */
    function toggleCompactMode() {
        const current = isCompactMode();
        setCompactMode(!current);
        return !current;
    }
    
    /**
     * Apply compact mode to the page
     */
    function applyCompactMode(enabled) {
        if (enabled) {
            document.body.classList.add('compact-mode');
        } else {
            document.body.classList.remove('compact-mode');
        }
    }
    
    /**
     * Get URL with compact mode parameter
     */
    function getUrlWithCompactMode(url, enabled) {
        const urlObj = new URL(url, window.location.origin);
        if (enabled) {
            urlObj.searchParams.set('compact', 'true');
        } else {
            urlObj.searchParams.delete('compact');
            urlObj.searchParams.delete('compact-mode');
            urlObj.searchParams.delete('pi');
        }
        return urlObj.toString();
    }
    
    /**
     * Update all links to preserve compact mode
     */
    function updateLinks() {
        const compact = isCompactMode();
        
        // Update all links with data-preserve-compact attribute
        document.querySelectorAll('a[data-preserve-compact]').forEach(link => {
            // Get the base path from href or pathname
            let basePath = link.pathname;
            const href = link.getAttribute('href');
            if (href) {
                // Extract pathname from href (handles both relative and absolute URLs)
                try {
                    const urlObj = new URL(href, window.location.origin);
                    basePath = urlObj.pathname;
                } catch (e) {
                    // If href is relative, use pathname from the link element
                    basePath = link.pathname;
                }
            }
            link.href = getUrlWithCompactMode(basePath, compact);
        });
    }
    
    /**
     * Initialize compact mode on page load
     */
    function init() {
        const compact = isCompactMode();
        applyCompactMode(compact);
        
        // Update links after DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', updateLinks);
        } else {
            updateLinks();
        }
    }
    
    // Initialize immediately
    init();
    
    // Export functions to window object
    window.CompactMode = {
        isEnabled: isCompactMode,
        set: setCompactMode,
        toggle: toggleCompactMode,
        getUrl: getUrlWithCompactMode,
        updateLinks: updateLinks
    };
    
    console.log('CompactMode utility loaded. Current state:', isCompactMode());
})();

