'use strict';

W.ns('W.pages');

W.pages.StrainSearchResultsPage = Class.extend({

    scrollPage: 2, // start from 2nd page because we already have 1st
    scrollSize: 8,

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
                    url: '/api/v1/search/result/?page={0}&size={1}'.format(that.scrollPage, that.scrollSize),
                    dataType: 'json',
                    success: function (data) {
                        that.scrollPage += 1;
                        var searchResults = data.search_results,
                            searchResultsTotal = data.search_results_total;

                        if (that.scrollPage * that.scrollSize >= searchResultsTotal) {
                            $('.search-result-footer-wrapper').addClass('hidden');
                        }

                        for (var i = 0; i < searchResults.length; i++) {
                            var position = '{0}{1}'.format(that.scrollPage, i);
                            that.ui.$searchResult.append(that.parseSearchResultItem(position, searchResults[i]));
                            that.initRating($('.loaded-rating-' + position));
                        }

                        that.ui.$loadingIcon.removeClass('rotating');
                    }
                });
            }
        });
    },

    parseSearchResultItem: function (position, item) {
        var that = this,
            compiled = _.template($('#strain-item-template').html());
        return compiled({
            'position': position,
            'strain': item,
            'closestDeliveryDistance': that.findClosestDeliveryDistance(item.delivery_addresses),
            'openClosedCount': that.countOpenCloseDeliveries(item.delivery_addresses)
        });
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

        return opened.length + ' Open, ' + closed.length + ' Closed';
    },

    initRatings: function () {
        var that = this;
        that.ui.$strainRating.each(function (position, el) {
            that.initRating($(el));
        });
    },

    initRating: function ($el) {
        var rating = $el.text();
        if (rating !== 'Not Rated') {
            $el.rateYo({
                rating: rating,
                readOnly: true,
                spacing: '1px',
                normalFill: '#aaa8a8', // $grey-light
                ratedFill: '#6bc331', // $avocado-green
                starWidth: '16px'
            });
        }
    }
});
