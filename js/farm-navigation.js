/**
 * Farm Navigation Script
 * Adds next/previous navigation based on drift/journey order
 */
(function() {
    'use strict';
    
    // Wait for drift navigation to load
    function initFarmNavigation() {
        if (!window.getDriftNeighbors) {
            setTimeout(initFarmNavigation, 100);
            return;
        }
        
        // Get current farm slug from URL
        const currentPath = window.location.pathname;
        const slugMatch = currentPath.match(/farms\/([^\/]+)\//);
        if (!slugMatch) return;
        
        const currentSlug = slugMatch[1];
        const result = window.getDriftNeighbors(currentSlug, 'farm');
        
        if (!result || (!result.previous && !result.next)) return;
        
        const navContainer = document.getElementById('farm-navigation');
        if (!navContainer) return;
        
        // Helper function to get URL for a stop based on its type
        function getUrlForStop(stop) {
            if (!stop || !stop.type) {
                // Fallback: try to determine from slug
                if (stop.slug === 'founderhaus' || stop.slug === 'black-king-ilheus') {
                    return '../../partners/' + stop.slug + '/index.html';
                } else if (window.FARMS_DATA && window.FARMS_DATA[stop.slug]) {
                    return '../' + stop.slug + '/index.html';
                } else if (stop.slug === 'coopercabruca' || stop.slug === 'cepotx') {
                    return '../../cooperatives/' + stop.slug + '/index.html';
                } else if (stop.slug === 'itacare-cultural-experiences' || stop.slug === 'salvador-colonial-history' || stop.slug === 'jungle-johnny-amazon-tours' || stop.slug === 'cargo-boat-manaus-leticia') {
                    // Map data slug to folder name for experiences
                    const slugToFolderMap = {
                        'itacare-cultural-experiences': 'itacare-cultural-immersion',
                        'salvador-colonial-history': 'salvador-colonial-history',
                        'jungle-johnny-amazon-tours': 'jungle-johnny-amazon-tours',
                        'cargo-boat-manaus-leticia': 'cargo-boat-manaus-leticia'
                    };
                    const folderName = slugToFolderMap[stop.slug] || stop.slug;
                    return '../../cacao-journeys/brazilian-path/experiences/' + folderName + '/index.html';
                } else {
                    return '../' + stop.slug + '/index.html';
                }
            }
            
            switch (stop.type) {
                case 'partner':
                    return '../../partners/' + stop.slug + '/index.html';
                case 'farm':
                    return '../' + stop.slug + '/index.html';
                case 'cooperative':
                    return '../../cooperatives/' + stop.slug + '/index.html';
                case 'experience':
                    // Map data slug to folder name
                    const slugToFolderMap = {
                        'itacare-cultural-experiences': 'itacare-cultural-immersion',
                        'salvador-colonial-history': 'salvador-colonial-history',
                        'jungle-johnny-amazon-tours': 'jungle-johnny-amazon-tours',
                        'cargo-boat-manaus-leticia': 'cargo-boat-manaus-leticia'
                    };
                    const folderName = slugToFolderMap[stop.slug] || stop.slug;
                    return '../../cacao-journeys/brazilian-path/experiences/' + folderName + '/index.html';
                default:
                    return '#';
            }
        }
        
        let navHTML = '';
        
        // Previous stop
        if (result.previous) {
            let prevUrl = getUrlForStop(result.previous);
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
        
        // Next stop
        if (result.next) {
            let nextUrl = getUrlForStop(result.next);
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

