'use strict';

W.ns('W.pages.locations');

W.pages.locations.LocationsList = Class.extend({

    ui: {
        $pageSelector: $('.page-letter')
    },

    regions: {
        $locations: $('.locations-wrapper')
    },

    templates: {
        location: _.template($('#location_template').html())
    },

    init: function init(options) {
        this.view = options && options.view;
        this.activeState = options && options.active_state;
        this.activeCity = options && options.active_city;

        this.initView();
    },

    initView: function initView() {
        if (this.view) {
            switch (this.view) {
                case 'city':
                    this.initCitiesView();
                    break;
                case 'state':
                    this.initStatesView();
                    break;
                default:
                    return;
            }
        }
    },

    initCitiesView: function initCitiesView() {
        var that = this;
        if (this.activeState && this.activeCity) {
            this.getPagedDispensaries(function (data) {
                that.pagedDispensaries = data;
                that.renderAllDispensaries();
                that.initScrollPager();
            });
        }
    },

    getPagedDispensaries: function getPagedCities(success) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/businesses/{0}/{1}'.format(this.activeState, this.activeCity),
            success: function (data) {
                success(data);
            }
        });
    },

    renderAllDispensaries: function renderPageByLetter() {
        if (this.pagedDispensaries) {
            var that = this,
                pages = this.pagedDispensaries,
                sorted = this.sortKeysBy(pages),
                Dispensary = this.templates.location;

            $.each(sorted, function (i, page) {
                if (i && i !== 'null' && page) {
                    that.regions.$locations.append('<div class="page" id="letter-{0}"></div>'.format(i.toLowerCase()));

                    var $pageWrapper = $('#letter-{0}'.format(i.toLowerCase()));

                    $.each(page, function (j, location) {
                        $pageWrapper.append(Dispensary({
                            d: location,
                            state: that.activeState,
                            city: that.activeCity,
                            formatLocation: that.formatLocation
                        }));
                    });

                    that.regions.$locations.append('<hr/>');
                }
            });
        } else {
            this.regions.$locations.html('No dispensaries found in this city.');
        }
    },

    formatLocation: function formatLocation(location) {
        return W.common.Format.formatAddress({
            street1: location.street1,
            city: location.city,
            state: location.state,
            zipcode: location.zip_code,
            location_raw: location.location_raw
        });
    },

    initStatesView: function initStatesView() {
        this.initScrollPager();
    },

    initScrollPager: function initScrollPager() {
        var that = this;
        this.ui.$pageSelector.on('click', function (e) {
            e.preventDefault();

            var $selectedPage = $(this),
                $scrollTo = $('#letter-{0}'.format($selectedPage.text().toLowerCase()));

            that.ui.$pageSelector.removeClass('active');
            $selectedPage.addClass('active');

            if ($scrollTo && $scrollTo.length > 0) {
                $scrollTo.get(0).scrollIntoView();
            }
        });
    },

    sortKeysBy: function sortKeysBy(obj, comparator) {
        var keys = _.sortBy(_.keys(obj), function (key) {
            return comparator ? comparator(obj[key], key) : key;
        });

        return _.object(keys, _.map(keys, function (key) {
            return obj[key];
        }));
    }

});