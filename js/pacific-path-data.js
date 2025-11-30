/**
 * Pacific West Coast Path Data
 * Contains experiences for the Pacific West Coast journey
 */
(function() {
    'use strict';
    
    if (window.PACIFIC_PATH_DATA) {
        return; // Already loaded
    }
    
    window.PACIFIC_PATH_DATA = {
        'slab-city-salvation-mountain': {
            name: 'Slab City & Salvation Mountain',
            slug: 'slab-city-salvation-mountain',
            lat: 33.2581,
            lon: -115.4650,
            location: 'Slab City, California (near Salton Sea)',
            type: 'experience',
            url: 'experiences/slab-city-salvation-mountain/index.html',
            season: 'Year-round, peak in winter',
            description: 'Experience Slab City, the "Last Free Place in America," and Salvation Mountain, a vibrant art installation in the California desert. This off-grid community near the Salton Sea offers a unique space where freedom, art, and community converge. Visit The Ponderosa, an off-grid homesteading haven run by Rodney "Spyder" and Shannon, where regenerative cacao creates connections in this unique desert community. This experience represents a powerful intersection of freedom, art, community, and conscious living.',
            venues: [
                {
                    name: 'The Ponderosa',
                    slug: 'the-ponderosa-slab-city',
                    url: '../../../../partners/the-ponderosa-slab-city/index.html',
                    description: 'An off-grid homesteading haven offering accommodations and gatherings'
                },
                {
                    name: 'Salvation Mountain',
                    description: 'Leonard Knight\'s massive art installation'
                },
                {
                    name: 'Slab City',
                    description: 'The off-grid community itself'
                }
            ],
            image: '../../assets/partners/headers/the-ponderosa-slab-city-header.jpg'
        },
        'winter-desert-gatherings': {
            name: 'Winter Desert Gatherings',
            slug: 'winter-desert-gatherings',
            lat: 33.6642,
            lon: -114.1300,
            location: 'Quartzite, Arizona & California Desert (Salton Sea, Joshua Tree)',
            type: 'experience',
            url: 'experiences/winter-desert-gatherings/index.html',
            season: 'Winter (Thanksgiving period through end of winter)',
            description: 'During the winter season, nomads migrate to the desert in Arizona Quartzite and California\'s Salton Sea and Joshua Tree areas, where vibrant gatherings bring communities together. Experience Tribe Boheme gathering, Van Aid, SchooliePalooza, Bombay Beach Binnelie, Boondockers bash, Rubber Tramp Rendezvous, and the Quartzite gem show—each a celebration of freedom, community, and conscious living. As the final destination of the Pacific West Coast journey, these winter desert gatherings offer a powerful culmination to the seasonal migration, where regenerative cacao creates spaces for connection, celebration, and transformation in the heart of the desert.',
            gatherings: [
                'Tribe Boheme gathering',
                'Van Aid',
                'SchooliePalooza',
                'Bombay Beach Binnelie',
                'Boondockers bash',
                'Rubber Tramp Rendezvous',
                'Quartzite gem show'
            ],
            facebookGroup: 'https://www.facebook.com/groups/1180376599189046/',
            image: '../../assets/partners/headers/winter-desert-gatherings-header.jpg'
        }
    };
})();

