'use strict';

W.ns('W.pages.dispensary');

W.pages.dispensary.DispensaryInfo = Class.extend({

    location: null,

    ui: {
        $businessId: $('#business_id'),
        $location_id: $('#location_id'),
        $strain_id: $('#strain_id')
    },

    regions: {
        $headerRegion: $('.header-region'),
        $contentRegion: $('.content-region')
    },

    templates: {
        $header: _.template($('#dispensary_header_template').html()),
        $content: _.template($('#dispensary_content_template').html())
    },

    init: function init() {
        var that = this;

        this.retrieveLocation(function (location) {
            if (location) {
                that.location = location;
                that.showHeader();
                that.showContent();
            }
        });
    },

    retrieveLocation: function retrieveLocation(successCallback) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/businesses/{0}/locations/{1}?ddp=true'.format(this.ui.$businessId.val(), this.ui.$location_id.val()),
            success: function (data) {
                successCallback(data.location);
            }
        });
    },

    showHeader: function showHeader() {
        this.regions.$headerRegion.append(this.templates.$header({
            l: this.location,
            formatAddressLine: this.formatAddressLine,
            getOpenDays: this.getOpenDays
        }));

        var $rawRating = $('.rating-raw');

        if ($rawRating && $rawRating.text() === 'Not Rated') {
            $rawRating.addClass('hidden');
        } else {
            W.common.Rating.readOnly($rawRating, {rating: $rawRating.text(), spacing: '5px', starWidth: '20px'});
        }

        this.clickRateLink();
        this.clickFavoriteIcon();
        this.clickPhoneNumberLink();
        this.clickPlaceOrderBtn();
        this.clickGetDirectionsBtn();
    },

    formatAddressLine: function formatAddressLine(location) {
        var parts = [];

        if (location.city) {
            parts.push(location.city);
        }

        if (location.state) {
            parts.push(location.state);
        }

        if (location.zip_code) {
            parts.push(location.zip_code);
        }

        return parts.join(', ');
    },

    getOpenDays: function getOpenDays(location) {
        var days = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'],
            dayNames = W.common.Constants.days,
            todayIndex = new Date().getDay(), // 0 - Sun, 6 - Sat
            toDisplay = [],
            open_time, close_time;

        $.each(days.slice(todayIndex, days.length), function (i, day) {
            var d = _.filter(dayNames, function (d) {
                return d.value === day ? d : null;
            });

            if (d && d[0]) {
                open_time = location['{0}_open'.format(d[0].value)];
                close_time = location['{0}_close'.format(d[0].value)];

                toDisplay.push({
                    day: d[0].name,
                    time: (open_time && close_time) ? '{0} - {1}'.format(open_time, close_time) : 'Closed',
                    first: i === 0
                });
            }
        });

        $.each(days.slice(0, todayIndex), function (i, day) {
            var d = _.filter(dayNames, function (d) {
                return d.value === day ? d : null;
            });

            if (d && d[0]) {
                open_time = location['{0}_open'.format(d[0].value)];
                close_time = location['{0}_close'.format(d[0].value)];

                toDisplay.push({
                    day: d[0].name,
                    time: (open_time && close_time) ? '{0} - {1}'.format(open_time, close_time) : 'Closed'
                });
            }
        });

        return toDisplay;
    },

    clickRateLink: function clickRateLink() {
        $('.rate-link').on('click', function (e) {
            e.preventDefault();
            // TODO
            alert('Rate Location');
        });
    },

    clickFavoriteIcon: function clickFavoriteIcon() {
        $('.location-like').on('click', function () {
            // TODO
            alert('Is Location favorite now: {0}'.format($(this).hasClass('active')));
        });
    },

    clickPhoneNumberLink: function clickPhoneNumberLink() {
        $('.phone-number').on('click', function (e) {
            // Fo mobile devices do not prevent 'tel:' default
            if ($(window).outerWidth() > 768) {
                e.preventDefault();
                // TODO
                alert('Show phone dialog');
            }
        });
    },

    clickPlaceOrderBtn: function clickPlaceOrderBtn() {
        var $btn = $('.btn-place-order');
        if ($btn && $btn.length != 0) {
            $btn.on('click', function () {
                // TODO
                alert('Place order. Show phone number dialog instead?')
            });
        }
    },

    clickGetDirectionsBtn: function clickGetDirectionsBtn() {
        var $btn = $('.btn-get-directions');
        if ($btn && $btn.length != 0) {
            $btn.on('click', function () {
                // TODO
                alert('Get Direction. Nothing in spec abot this.')
            });
        }
    },

    showContent: function showContent() {
        var that = this;
        $.when(this.getMenuItemsDeferred(), this.getReviewsDeferred())
            .done(function (menu_response, reviews_response) {
                that.menu_items = menu_response && menu_response[0]['menu'];
                that.reviews = reviews_response && reviews_response[0]['reviews'];

                that.menu_sativas = that.getSortedMenuItems('sativa');
                that.menu_indicas = that.getSortedMenuItems('indica');
                that.menu_hybrids = that.getSortedMenuItems('hybrid');

                that.regions.$contentRegion.append(that.templates.$content({
                    l: that.location,
                    sativas: that.menu_sativas,
                    indicas: that.menu_indicas,
                    hybrids: that.menu_hybrids,
                    selectedStrainMenuItem: that.selectedStrainMenuItem,
                    formatPrice: that.formatPrice,
                    formatScore: that.formatScore,
                    reviews: that.reviews,
                    deals: []
                }));
            });
    },

    getMenuItemsDeferred: function getMenuItemsDeferred() {
        return $.ajax({
            method: 'GET',
            url: '/api/v1/businesses/{0}/locations/{1}/menu?ddp=true'.format(this.ui.$businessId.val(), this.ui.$location_id.val())
        });
    },

    getReviewsDeferred: function getReviewsDeferred() {
        return $.ajax({
            method: 'GET',
            url: '/api/v1/businesses/{0}/locations/{1}/reviews'.format(this.ui.$businessId.val(), this.ui.$location_id.val())
        });
    },

    getSortedMenuItems: function getSortedMenuItems(type) {
        if (this.menu_items && this.menu_items.length > 0) {
            var that = this,
                strainId = parseInt(this.ui.$strain_id.val(), 10),
                filtered = _.filter(this.menu_items, function (item) {
                    if (parseInt(item.strain_id, 10) === strainId) {
                        that.selectedStrainMenuItem = item;
                    }

                    if (item.strain_variety === type) {
                        return item;
                    }
                });
            filtered.sort(this.sortMenuItems);
            return filtered;
        }

        return [];
    },

    sortMenuItems: function sortMenuItems(el1, el2) {
        var aScore = el1.match_score, bScore = el2.match_score;
        return aScore < bScore ? 1 : aScore > bScore ? -1 : 0;
    },

    formatPrice: function formatPrice(price) {
        return price ? '${0}'.format(price) : '--';
    },

    formatScore: function formatScore(score) {
        return score ? '{0}%'.format(score) : '--';
    }
});
