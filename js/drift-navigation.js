/**
 * Drift Navigation Script
 * Provides navigation based on drift/journey order instead of traveling salesman
 */

(function() {
    'use strict';
    
    // Get Pacific West Coast Drift order (North to South)
    function getPacificWestCoastDriftOrder() {
        if (!window.PARTNERS_DATA) return [];
        
        const westCoastStates = ['Washington', 'Oregon', 'California', 'Arizona'];
        const filtered = {};
        
        for (const slug in window.PARTNERS_DATA) {
            const partner = window.PARTNERS_DATA[slug];
            const location = partner.location.toLowerCase();
            const isWestCoast = westCoastStates.some(state => 
                location.includes(state.toLowerCase())
            );
            if (isWestCoast) {
                filtered[slug] = partner;
            }
        }
        
        // Sort North to South (latitude descending)
        const slugs = Object.keys(filtered);
        return slugs.sort((a, b) => filtered[b].lat - filtered[a].lat);
    }
    
    // Get Brazilian Drift order (South to North: Founderhaus, then farms)
    // This matches the exact order from the Brazilian path page (sorted by latitude ascending)
    function getBrazilianDriftOrder() {
        // Define the exact order matching the Brazilian path page itinerary
        // Sorted South to North (latitude ascending: -27.4305 to -3.3922222)
        const exactOrder = [
            'founderhaus',                    // -27.4305 (Florianópolis) - Starting point
            'fazenda-capelavelha-bahia',      // -14.6173663 (Bahia)
            'fazenda-santa-ana-bahia',        // -14.3225976 (Bahia)
            'vivi-jesus-do-deus-itacare',    // -14.324474 (Itacaré, Bahia)
            'oscar-bahia',                    // -12.9714 (Bahia)
            'paulo-la-do-sitio-para'          // -3.3922222 (Pará, Amazon) - Northernmost
        ];
        
        return exactOrder;
    }
    
    // Get neighbors in drift order
    function getDriftNeighbors(currentSlug, isPartner) {
        let order = [];
        let journeyUrl = '';
        
        if (isPartner) {
            // Check if partner is in Pacific West Coast drift
            const pacificOrder = getPacificWestCoastDriftOrder();
            if (pacificOrder.includes(currentSlug)) {
                order = pacificOrder;
                journeyUrl = '../../cacao-journeys/pacific-west-coast-path/index.html';
            } else if (currentSlug === 'founderhaus') {
                // Founderhaus is in Brazilian drift
                order = getBrazilianDriftOrder();
                journeyUrl = '../../cacao-journeys/brazilian-path/index.html';
            } else {
                // Partner not in any drift - return null
                return { previous: null, next: null, journeyUrl: null };
            }
        } else {
            // Farm - check if in Brazilian drift
            order = getBrazilianDriftOrder();
            if (order.includes(currentSlug)) {
                journeyUrl = '../../cacao-journeys/brazilian-path/index.html';
            } else {
                return { previous: null, next: null, journeyUrl: null };
            }
        }
        
        const currentIndex = order.indexOf(currentSlug);
        if (currentIndex === -1) {
            return { previous: null, next: null, journeyUrl: null };
        }
        
        const prevSlug = currentIndex > 0 ? order[currentIndex - 1] : null;
        const nextSlug = currentIndex < order.length - 1 ? order[currentIndex + 1] : null;
        
        let previous = null;
        let next = null;
        
        if (prevSlug) {
            if (prevSlug === 'founderhaus') {
                previous = window.PARTNERS_DATA ? window.PARTNERS_DATA[prevSlug] : null;
            } else if (window.FARMS_DATA && window.FARMS_DATA[prevSlug]) {
                // Previous is a farm
                previous = window.FARMS_DATA[prevSlug];
            } else if (window.PARTNERS_DATA && window.PARTNERS_DATA[prevSlug]) {
                // Previous is a partner
                previous = window.PARTNERS_DATA[prevSlug];
            }
        }
        
        if (nextSlug) {
            if (nextSlug === 'founderhaus') {
                next = window.PARTNERS_DATA ? window.PARTNERS_DATA[nextSlug] : null;
            } else if (window.FARMS_DATA && window.FARMS_DATA[nextSlug]) {
                // Next is a farm
                next = window.FARMS_DATA[nextSlug];
            } else if (window.PARTNERS_DATA && window.PARTNERS_DATA[nextSlug]) {
                // Next is a partner
                next = window.PARTNERS_DATA[nextSlug];
            }
        }
        
        return { previous, next, journeyUrl };
    }
    
    // Expose to window
    window.getDriftNeighbors = getDriftNeighbors;
    window.getPacificWestCoastDriftOrder = getPacificWestCoastDriftOrder;
    window.getBrazilianDriftOrder = getBrazilianDriftOrder;
})();

