/**
 * Farm Navigation Script
 * Adds next/previous navigation based on drift/journey order
 */
(function() {
    'use strict';
    
    // Wait for farms data and drift navigation to load
    function initFarmNavigation() {
        if (!window.FARMS_DATA || !window.getDriftNeighbors) {
            setTimeout(initFarmNavigation, 100);
            return;
        }
        
        // Get current farm slug from URL
        const currentPath = window.location.pathname;
        const slugMatch = currentPath.match(/farms\/([^\/]+)\//);
        if (!slugMatch) return;
        
        const currentSlug = slugMatch[1];
        const result = window.getDriftNeighbors(currentSlug, false);
        
        if (!result || (!result.previous && !result.next)) return;
        
        const navContainer = document.getElementById('farm-navigation');
        if (!navContainer) return;
        
        let navHTML = '';
        
        // Previous stop (could be farm or Founderhaus)
        if (result.previous) {
            let prevUrl = '';
            if (result.previous.slug === 'founderhaus') {
                prevUrl = '../../partners/founderhaus/index.html';
            } else {
                prevUrl = '../' + result.previous.slug + '/index.html';
            }
            navHTML += '<a href="' + prevUrl + '" class="farm-nav-link previous">';
            navHTML += '<span class="farm-nav-label">← Previous</span>';
            navHTML += '<span class="farm-nav-name">' + result.previous.name + '</span>';
            navHTML += '</a>';
        } else {
            navHTML += '<div class="farm-nav-link previous disabled">';
            navHTML += '<span class="farm-nav-label">← Previous</span>';
            navHTML += '<span class="farm-nav-name">—</span>';
            navHTML += '</div>';
        }
        
        // Next stop (could be farm or Founderhaus)
        if (result.next) {
            let nextUrl = '';
            if (result.next.slug === 'founderhaus') {
                nextUrl = '../../partners/founderhaus/index.html';
            } else {
                nextUrl = '../' + result.next.slug + '/index.html';
            }
            navHTML += '<a href="' + nextUrl + '" class="farm-nav-link next">';
            navHTML += '<span class="farm-nav-label">Next →</span>';
            navHTML += '<span class="farm-nav-name">' + result.next.name + '</span>';
            navHTML += '</a>';
        } else {
            navHTML += '<div class="farm-nav-link next disabled">';
            navHTML += '<span class="farm-nav-label">Next →</span>';
            navHTML += '<span class="farm-nav-name">—</span>';
            navHTML += '</div>';
        }
        
        navContainer.innerHTML = navHTML;
        
        // Update back link if journey URL is available
        if (result.journeyUrl) {
            const backLink = document.querySelector('.back-link');
            if (backLink) {
                backLink.href = result.journeyUrl;
                backLink.textContent = 'Back to Journey';
            }
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFarmNavigation);
    } else {
        initFarmNavigation();
    }
})();

