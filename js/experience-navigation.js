/**
 * Experience Navigation Script
 * Adds next/previous navigation based on drift/journey order
 */
(function() {
    'use strict';
    
    // Wait for data and drift navigation to load
    function initExperienceNavigation() {
        if (!window.getDriftNeighbors) {
            setTimeout(initExperienceNavigation, 100);
            return;
        }
        
        // Get current experience slug from URL
        const currentPath = window.location.pathname;
        const slugMatch = currentPath.match(/experiences\/([^\/]+)\//);
        if (!slugMatch) return;
        
        // Map folder names to data slugs
        const folderToSlugMap = {
            'itacare-cultural-immersion': 'itacare-cultural-experiences',
            'salvador-colonial-history': 'salvador-colonial-history',
            'jungle-johnny-amazon-tours': 'jungle-johnny-amazon-tours',
            'cargo-boat-manaus-leticia': 'cargo-boat-manaus-leticia',
            'slab-city-salvation-mountain': 'slab-city-salvation-mountain',
            'winter-desert-gatherings': 'winter-desert-gatherings'
        };
        
        const folderName = slugMatch[1];
        const currentSlug = folderToSlugMap[folderName] || folderName;
        
        // Determine which journey path we're in based on URL
        const isPacificPath = currentPath.includes('/pacific-west-coast-path/');
        
        const result = window.getDriftNeighbors(currentSlug, 'experience');
        
        if (!result || (!result.previous && !result.next)) return;
        
        const navContainer = document.getElementById('experience-navigation');
        if (!navContainer) return;
        
        let navHTML = '';
        
        // Previous stop
        if (result.previous) {
            let prevUrl = getUrlForStop(result.previous);
            navHTML += '<a href="' + prevUrl + '" class="experience-nav-link previous">';
            navHTML += '<span class="experience-nav-label">← Previous</span>';
            navHTML += '<span class="experience-nav-name">' + result.previous.name + '</span>';
            navHTML += '</a>';
        } else {
            navHTML += '<div class="experience-nav-link previous disabled">';
            navHTML += '<span class="experience-nav-label">← Previous</span>';
            navHTML += '<span class="experience-nav-name">—</span>';
            navHTML += '</div>';
        }
        
        // Next stop
        if (result.next) {
            let nextUrl = getUrlForStop(result.next);
            navHTML += '<a href="' + nextUrl + '" class="experience-nav-link next">';
            navHTML += '<span class="experience-nav-label">Next →</span>';
            navHTML += '<span class="experience-nav-name">' + result.next.name + '</span>';
            navHTML += '</a>';
        } else {
            navHTML += '<div class="experience-nav-link next disabled">';
            navHTML += '<span class="experience-nav-label">Next →</span>';
            navHTML += '<span class="experience-nav-name">—</span>';
            navHTML += '</div>';
        }
        
        navContainer.innerHTML = navHTML;
        
        // Update back link if journey URL is available
        // For experience pages, the journey URL should be relative to the experience folder
        const backLink = document.querySelector('.back-link');
        if (backLink) {
            // Experience pages are in experiences/[name]/, so journey is 2 levels up
            if (isPacificPath) {
                backLink.href = '../../index.html';
                backLink.textContent = 'Back to Pacific West Coast Journey';
            } else {
                backLink.href = '../../index.html';
                backLink.textContent = 'Back to Brazilian Journey';
            }
        }
    }
    
    // Helper function to get URL for a stop based on its type
    function getUrlForStop(stop) {
        if (!stop) {
            return '#';
        }
        
        // Check if it's a known partner (even if type is missing)
        if (window.PARTNERS_DATA && window.PARTNERS_DATA[stop.slug]) {
            if (stop.slug === 'founderhaus') {
                return '../../../../partners/founderhaus/index.html';
            } else {
                return '../../../../partners/' + stop.slug + '/index.html';
            }
        }
        
        // Check if it's a known experience
        if (stop.slug === 'slab-city-salvation-mountain' || stop.slug === 'winter-desert-gatherings') {
            return '../' + stop.slug + '/index.html';
        }
        
        if (stop.slug === 'itacare-cultural-experiences' || stop.slug === 'salvador-colonial-history' || stop.slug === 'jungle-johnny-amazon-tours' || stop.slug === 'cargo-boat-manaus-leticia') {
            const slugToFolderMap = {
                'itacare-cultural-experiences': 'itacare-cultural-immersion',
                'salvador-colonial-history': 'salvador-colonial-history',
                'jungle-johnny-amazon-tours': 'jungle-johnny-amazon-tours',
                'cargo-boat-manaus-leticia': 'cargo-boat-manaus-leticia'
            };
            const folderName = slugToFolderMap[stop.slug] || stop.slug;
            return '../' + folderName + '/index.html';
        }
        
        if (!stop.type) {
            // Fallback: try to determine from slug
            if (stop.slug === 'founderhaus' || stop.slug === 'black-king-ilheus') {
                return '../../../../partners/' + stop.slug + '/index.html';
            } else if (window.FARMS_DATA && window.FARMS_DATA[stop.slug]) {
                return '../../../../farms/' + stop.slug + '/index.html';
            } else if (stop.slug === 'coopercabruca' || stop.slug === 'cepotx') {
                return '../../../../cooperatives/' + stop.slug + '/index.html';
            } else {
                return '../' + stop.slug + '/index.html';
            }
        }
        
        switch (stop.type) {
            case 'partner':
                // Determine if it's Pacific or Brazilian path based on context
                const isPacificPath = window.location.pathname.includes('/pacific-west-coast-path/');
                if (stop.slug === 'founderhaus') {
                    return '../../../../partners/founderhaus/index.html';
                } else {
                    return '../../../../partners/' + stop.slug + '/index.html';
                }
            case 'farm':
                return '../../../../farms/' + stop.slug + '/index.html';
            case 'cooperative':
                return '../../../../cooperatives/' + stop.slug + '/index.html';
            case 'experience':
                // Map data slug to folder name
                const slugToFolderMap = {
                    'itacare-cultural-experiences': 'itacare-cultural-immersion',
                    'salvador-colonial-history': 'salvador-colonial-history',
                    'jungle-johnny-amazon-tours': 'jungle-johnny-amazon-tours',
                    'cargo-boat-manaus-leticia': 'cargo-boat-manaus-leticia',
                    'slab-city-salvation-mountain': 'slab-city-salvation-mountain',
                    'winter-desert-gatherings': 'winter-desert-gatherings'
                };
                const folderName = slugToFolderMap[stop.slug] || stop.slug;
                return '../' + folderName + '/index.html';
            default:
                return '#';
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initExperienceNavigation);
    } else {
        initExperienceNavigation();
    }
})();

