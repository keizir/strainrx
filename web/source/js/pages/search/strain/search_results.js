'use strict';

W.ns('W.pages');

W.pages.StrainSearchResultsPage = Class.extend({

    scrollPage: 1,
    scrollSize: 20,
    currentFilter: 'all', // local, delivery

    locations: {},
    deliveries: {},

    templates: {
        expandedLocations: _.template($('#expanded-locations-template').html()),
        expandedLocation: _.template($('#expanded-location-template').html())
    },

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
        var that = this;
        this.name = 'StrainSearchResultsPage';

        this.getSearchResults('all', function () {
            that.buildSortMenu();
            that.handleScrollPage();
            that.initRatings();
        });

        W.subscribe.apply(this);
    },

    _on_close_popup: function _on_close_popup() {
        this.closeOpenedLocationDropdowns();
    },

    closeOpenedLocationDropdowns: function closeOpenedLocationDropdowns() {
        var $menuExpanderButtons = $('.item-locations, .item-deliveries'),
            $expandedAreas = $('.locations-expanded');

        $.each($menuExpanderButtons, function (i, el) {
            var $this = $(el);
            $this.removeClass('expanded');
            $this.css('z-index', 0);
        });

        $.each($expandedAreas, function (i, el) {
            var $this = $(el);
            $this.addClass('hidden');
            $this.html('');
        });
    },

    getSearchResults: function getSearchResults(filterType, success) {
        var that = this;
        this.ui.$loadingIcon.addClass('rotating');
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/result/?filter={0}&page={1}&size={2}'.format(filterType, that.scrollPage, that.scrollSize),
            dataType: 'json',
            success: function (data) {
                var searchResults = data.search_results,
                    searchResultsTotal = data.search_results_total;

                if (that.scrollPage * that.scrollSize >= searchResultsTotal) {
                    $('.search-result-footer-wrapper').addClass('hidden');
                }

                if (searchResults.length === 0 && searchResultsTotal === 0) {
                    that.ui.$searchResult.append('<h2>No Results Found</h2>');
                } else {
                    for (var i = 0; i < searchResults.length; i++) {
                        var position = '{0}{1}'.format(that.scrollPage, i);

                        that.ui.$searchResult.append(that.parseSearchResultItem(position, searchResults[i]));

                        that.locations[position] = searchResults[i].locations;
                        that.deliveries[position] = searchResults[i].deliveries;

                        that.initRating($('.loaded-rating-{0}'.format(position)));
                        that.clickLocations($('.locations-{0}'.format(position)), position, true);
                        that.clickLocations($('.deliveries-{0}'.format(position)), position, false);
                    }

                    that.ui.$loadingIcon.removeClass('rotating');
                    that.scrollPage += 1;
                }

                if (success) {
                    success();
                }
            }
        });
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
            var $el = $(this),
                filter = $el.attr('filter');

            that.ui.$menuActiveLink.text($el.find('a').text());
            that.ui.$menuActiveLink.attr('filter', filter);
            that.ui.$menuFilter.removeClass('expanded');
            that.ui.$menuHiddenLinks.addClass('hidden');
            that.applyNewFilter(filter);
        });

        that.ui.$menuActiveLink.on('click', function (e) {
            e.preventDefault();
            that.ui.$menuHiddenLinks.toggleClass('hidden');
            that.ui.$menuFilter.toggleClass('expanded');
        });
    },

    applyNewFilter: function applyNewFilter(filter) {
        this.scrollPage = 1;
        this.locations = {};
        this.deliveries = {};
        this.ui.$searchResult.html('');
        this.currentFilter = filter;
        this.ui.$searchResultFooterRegion.removeClass('hidden');
        this.getSearchResults(this.currentFilter);
    },

    handleScrollPage: function () {
        var that = this;
        this.ui.$window.on('scroll', function () {
            // End of the document reached?
            var hasMoreResultToShow = !that.ui.$searchResultFooterRegion.hasClass('hidden');
            if (that.ui.$document.height() - that.ui.$window.height() == that.ui.$window.scrollTop() && hasMoreResultToShow) {
                that.getSearchResults(that.currentFilter);
            }
        });
    },

    parseSearchResultItem: function (position, item) {
        var that = this,
            compiled = _.template($('#strain-item-template').html());
        return compiled({
            'position': position,
            'strain': item,
            'closestDistance': that.findClosestDistance,
            'openClosedCount': that.countOpenClosed
        });
    },

    findClosestDistance: function findClosestDistance(locations) {
        var distances = [], min;
        if (locations && locations.length > 0) {
            for (var i = 0; i < locations.length; i++) {
                distances.push(locations[i].distance);
            }
            min = Math.min.apply(Math, distances);
            return 'Nearest {0}mi'.format(Math.round(min * 100) / 100);
        }
    },

    countOpenClosed: function countOpenClosed(locations) {
        var opened = [], closed = [];
        if (locations && locations.length > 0) {
            for (var i = 0; i < locations.length; i++) {
                if (locations[i].open) {
                    opened.push(i);
                } else {
                    closed.push(i);
                }
            }

            if (opened.length > 0 && closed.length > 0) {
                return '{0} Open, {1} Closed'.format(opened.length, closed.length);
            }

            if (opened.length > 0 && closed.length == 0) {
                return '{0} Open'.format(opened.length);
            }

            if (opened.length == 0 && closed.length > 0) {
                return '{0} Closed'.format(closed.length);
            }
        }
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
    },

    clickLocations: function clickLocations($el, position, isLocations) {
        var that = this;
        $el.on('click', function () {
            var $this = $(this),
                position = $this.attr('position'),
                locations = isLocations ? that.locations[position] : that.deliveries[position],
                $exp = isLocations ? $('.locations-expanded-{0}'.format(position)) : $('.deliveries-expanded-{0}'.format(position));

            if (locations.length > 0) {
                if ($this.hasClass('expanded')) {
                    $this.removeClass('expanded');
                    $this.css('z-index', 0);
                    $exp.addClass('hidden');
                    $exp.html('');
                } else {
                    that.closeOpenedLocationDropdowns();
                    that.showLocations($this, $exp, isLocations, locations, position);
                }
            } else {
                that.closeOpenedLocationDropdowns();
            }
        });
    },

    showLocations: function showLocations($this, $exp, isLocations, locations, position) {
        var that = this, $priceExpander, $priceSort;

        $this.addClass('expanded');
        $this.css('z-index', 11);
        $exp.removeClass('hidden');
        $exp.html(that.templates.expandedLocations({
            'locations': locations,
            'formatDistance': that.formatDistance,
            'formatPrice': that.formatPrice,
            'renderLocation': that.templates.expandedLocation
        }));

        $.each($exp.find('.location-rating-exp'), function (i, el) {
            that.initRating($(el));
        });

        $priceExpander = $('.price-expander');
        $priceExpander.on('click', function () {
            $('.prices-wrapper').toggleClass('hidden');
        });

        $('.prices-wrapper').mouseleave(function () {
            $(this).addClass('hidden');
        });

        $('.price').on('click', function () {
            $('.prices-wrapper').addClass('hidden');
            var priceType = $(this).attr('id');
            $('.price-value').each(function (index, $el) {
                var $price = $($el);
                if ($price.attr('id') === priceType) {
                    $price.addClass('active');
                } else {
                    $price.removeClass('active');
                }
            });
        });

        $priceSort = $('.price-sort');
        $priceSort.on('click', function () {
            that.sortByPrice($priceSort, isLocations, position);
        });
    },

    renderLocation: function renderLocation(location) {
        return this.templates.expandedLocation({
            'l': location,
            'formatDistance': this.formatDistance,
            'formatPrice': this.formatPrice
        });
    },

    sortByPrice: function sortByPrice($priceSort, isLocations, position) {
        var that = this, newSort, fieldName = $('.price-value.active').attr('id'), url;

        if ($priceSort.hasClass('fa-caret-down')) {
            newSort = 'desc';
            $priceSort.removeClass('fa-caret-down');
            $priceSort.addClass('fa-caret-up');
        } else {
            newSort = 'asc';
            $priceSort.removeClass('fa-caret-up');
            $priceSort.addClass('fa-caret-down');
        }

        url = '/api/v1/search/strain/{0}/deliveries?filter={1}&order_field={2}&order_dir={3}&location_type={4}'
            .format($('#strain-id-{0}'.format(position)).val(), this.ui.$menuActiveLink.attr('filter'),
                fieldName, newSort, isLocations ? 'dispensary' : 'delivery');

        $.ajax({
            method: 'GET',
            url: url,
            success: function (data) {
                if (data && data.locations) {
                    var $expandedHolder = $('.expanded-locations-holder');
                    $expandedHolder.html('');

                    $.each(data.locations, function (i, l) {
                        $expandedHolder.append(that.renderLocation(l));
                    });

                    $.each($expandedHolder.find('.location-rating-exp'), function (i, el) {
                        that.initRating($(el));
                    });

                    $.each($('.price'), function () {
                        var $el = $(this);
                        if ($el.attr('id') === fieldName) {
                            $el.trigger('click');
                        }
                    });
                }
            }
        });
    },

    formatDistance: function formatDistance(d) {
        return '({0}mi)'.format(Math.round(d * 100) / 100);
    },

    formatPrice: function formatPrice(p) {
        return p ? '${0}'.format(p) : 'n/a';
    }
});
