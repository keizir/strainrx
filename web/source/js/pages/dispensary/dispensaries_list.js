'use strict';

W.ns('W.pages.dispensary');

W.pages.dispensary.DispensariesList = Class.extend({

    ui: {
        $pageSelector: $('.page-letter')
    },

    regions: {
        $dispensaries: $('.dispensaries-wrapper')
    },

    templates: {
        dispensary: _.template($('#dispensary_template').html())
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
                Dispensary = this.templates.dispensary;

            $.each(sorted, function (i, page) {
                if (i && i !== 'null' && page) {
                    that.regions.$dispensaries.append('<div class="page" id="letter-{0}"></div>'.format(i.toLowerCase()));

                    var $pageWrapper = $('#letter-{0}'.format(i.toLowerCase()));

                    $.each(page, function (j, dispensary) {
                        $pageWrapper.append(Dispensary({
                            d: dispensary,
                            state: that.activeState,
                            city: that.activeCity,
                            formatLocation: that.formatLocation
                        }));
                    });

                    that.regions.$dispensaries.append('<hr/>');
                }
            });
        } else {
            this.regions.$dispensaries.html('No dispensaries found in this city.');
        }
    },

    formatLocation: function formatLocation(dispensary) {
        return W.common.Format.formatAddress({
            street1: dispensary.street1,
            city: dispensary.city,
            state: dispensary.state,
            zipcode: dispensary.zip_code,
            location_raw: dispensary.location_raw
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