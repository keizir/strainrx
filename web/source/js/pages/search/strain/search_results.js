'use strict';

W.ns('W.pages');

W.pages.StrainSearchResultsPage = Class.extend({

    scrollPage: 0,

    ui: {
        $document: $(document),
        $window: $(window),
        $searchResultFooterRegion: $('.search-result-footer-wrapper'),

        $menuExpander: $('.menu-expander'),
        $menuHiddenLinks: $('.hidden-links'),
        $menuFilter: $('.filter-menu'),
        $menuLink: $('.menu-link'),
        $menuActiveLink: $('.menu-active-link a'),

        $strainRating: $('.strain-rating'),
        $searchResult: $('.search-result'),
        $loadingIcon: $('.scroll-icon i')
    },

    init: function () {
        this.buildSortMenu();
        this.handleScrollPage();
        this.initRatings();
    },

    buildSortMenu: function () {
        var that = this;

        that.ui.$menuExpander.on('click', function () {
            that.ui.$menuHiddenLinks.toggleClass('hidden');
            that.ui.$menuFilter.toggleClass('expanded');
        });

        that.ui.$menuFilter.mouseleave(function () {
            that.ui.$menuHiddenLinks.addClass('hidden');
            that.ui.$menuFilter.removeClass('expanded');
        });

        that.ui.$menuLink.on('click', function (e) {
            e.preventDefault();
            that.ui.$menuActiveLink.text($(this).find('a').text());
            that.ui.$menuFilter.removeClass('expanded');
            that.ui.$menuHiddenLinks.addClass('hidden');
        });

        that.ui.$menuActiveLink.on('click', function (e) {
            e.preventDefault();
            alert('Applying ' + $(this).text() + ' filter.'); // TODO remove this when backend ready
        });
    },

    handleScrollPage: function () {
        var that = this;

        this.ui.$window.on('scroll', function () {
            // End of the document reached?
            var hasMoreResultToShow = !that.ui.$searchResultFooterRegion.hasClass('hidden');
            if (that.ui.$document.height() - that.ui.$window.height() == that.ui.$window.scrollTop() && hasMoreResultToShow) {
                $('.scroll-icon i').addClass('rotating');

                $.ajax({
                    method: 'GET',
                    url: '/api/v1/search/result/?page=' + that.scrollPage + '&size=8',
                    dataType: 'json',
                    success: function (data) {
                        that.scrollPage += 1;
                        var searchResults = data.search_results,
                            searchResultsTotal = data.search_results_total;

                        // TODO remove this setTimeout. Used just for dummy data
                        setTimeout(function () {
                            if (that.scrollPage * 8 >= searchResultsTotal) {
                                $('.search-result-footer-wrapper').addClass('hidden');
                            }

                            for (var i = 0; i < searchResults.length; i++) {
                                that.ui.$searchResult.append(that.parseSearchResultItem(i, searchResults[i]));
                                that.initRating($('.loaded-rating-' + i));
                            }

                            that.ui.$loadingIcon.removeClass('rotating');
                        }, 2000);
                    }
                });
            }
        });
    },

    parseSearchResultItem: function (position, item) {
        var imageElement = item.image ? '<img src="' + item.image.image.url + '" alt="Strain Image">' :
            '<img src="/static/images/weed_small.jpg" alt="Strain Image">';

        return '<div class="result-item">' +
            '<div class="item-info-wrapper inline-block">' +
            '<div class="item-image inline-block">' +
            imageElement +
            '</div>' +
            '<div class="item-info inline-block">' +
            '<span class="strain-name">' +
            '<a href="#">' + item.name + '</a>' +
            '</span>' +
            '<span class="strain-type">' + item.type + '</span>' +
            '<span class="strain-rating loaded-rating-' + position + '">' + item.rating + '</span>' +
            '</div>' +
            '</div>' +
            '<div class="separator inline-block"></div>' +
            '<div class="item-locations inline-block">' +
            '<span class="locations-icon">' +
            '<i class="fa fa-map-marker fa-2x" aria-hidden="true"></i>' +
            '</span>' +
            '<span class="locations">' +
            '<span>' + item.delivery_addresses.length + ' Locations</span>' +
            '<span>' + this.findClosestDeliveryDistance(item.delivery_addresses) + '</span>' +
            '<span>' + this.countOpenCloseDeliveries(item.delivery_addresses) + '</span>' +
            '</span>' +
            '</div>' +
            '<div class="separator inline-block"></div>' +
            '<div class="item-deliveries inline-block">' +
            '<span class="deliveries-icon">' +
            '<i class="fa fa-truck fa-2x" aria-hidden="true"></i>' +
            '</span>' +
            '<span class="deliveries">' +
            '<span>1 Delivery Service Closed</span>' +
            '</span>' +
            '</div>' +
            '<div class="separator inline-block"></div>' +
            '<div class="item-percentage-match inline-block">' +
            '<span class="percentage">' + item.match_percentage + '%</span>' +
            '<span class="match">match</span>' +
            '</div>' +
            '</div>';
    },

    findClosestDeliveryDistance: function (dispensaries) {
        var distances = [],
            min;

        for (var i = 0; i < dispensaries.length; i++) {
            distances.push(dispensaries[i].distance);
        }

        min = Math.min.apply(Math, distances);
        return 'Nearest ' + Math.round(min * 100) / 100 + 'mi';
    },

    countOpenCloseDeliveries: function (dispensaries) {
        var opened = [],
            closed = [];

        for (var i = 0; i < dispensaries.length; i++) {
            if (dispensaries[i].open === 'true') {
                opened.push(i);
            } else if (dispensaries[i].open === 'false') {
                closed.push(i);
            }
        }

        return opened.length + ' Open, ' + closed.length + ' Close';
    },

    initRatings: function () {
        var that = this;
        that.ui.$strainRating.each(function (position, el) {
            that.initRating($(el));
        });
    },

    initRating: function ($el) {
        var rating = $el.text();
        $el.rateYo({
            rating: rating,
            readOnly: true,
            spacing: '1px',
            normalFill: '#aaa8a8', // $grey-light
            ratedFill: '#6bc331', // $avocado-green
            starWidth: '16px'
        });
    }
});
