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
                that.renderPageByLetter('A');
                that.initDispensariesPager();
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

    renderPageByLetter: function renderPageByLetter(letter) {
        if (this.pagedDispensaries && this.pagedDispensaries[letter]) {
            var that = this,
                dispensaries = this.pagedDispensaries[letter],
                Dispensary = this.templates.dispensary;

            that.regions.$dispensaries.html('');

            $.each(dispensaries, function (i, d) {
                that.regions.$dispensaries.append(Dispensary({
                    d: d,
                    state: that.activeState,
                    city: that.activeCity,
                    formatLocation: that.formatLocation
                }));
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

    initDispensariesPager: function initDispensariesPager() {
        var that = this;
        this.ui.$pageSelector.on('click', function (e) {
            e.preventDefault();
            var $selectedPage = $(this);
            that.ui.$pageSelector.removeClass('active');
            $selectedPage.addClass('active');
            that.renderPageByLetter($selectedPage.text());
        });
    },

    initStatesView: function initStatesView() {
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
    }

});