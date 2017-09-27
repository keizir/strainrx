'use strict';

W.ns('W.pages.dispensary');

W.pages.dispensary.Dispensaries = Class.extend({
    init: function init(options) {
        this.location = options && options.location;
        this.authenticated = options && options.authenticated;
        this.userId = options && options.userId;
        this.dispTimezone = null;
        this.dispLocation = null;

        this.initDispensaryLookupField();
        this.preFillUserLocation();
        this.initLocation();
        this.initDispLocation();
        this.initEventHandlers();
    },
    initDispensaryLookupField: function initDispensaryLookupField() {
        //var lookupTemplate = _.template($('#dispensary-lookup-field').html());
        //$('.dispensary-name-field').html(lookupTemplate({
        //    'lookup_placeholder': 'Search Dispensaries by Name'
        //}));
        new W.pages.dispensary.DispensaryLookup();
    },
    preFillUserLocation: function preFillUserLocation() {
        if (this.location) {
            $('.your-location-value').val(W.common.Format.formatAddress(this.location)).trigger('change');
        }
    },
    initEventHandlers: function initEventHandlers() {
        var that = this;

        $('.lookup-submit').on('click', function (e) {
            e.preventDefault();
            that.navigateToDispDetailPage();
        });

        $(document).on('keyup', function (e) {
            if (e.keyCode === 13) { // Enter Key
                that.navigateToDispDetailPage();
            }
        });
    },
    initLocation: function initLocation() {
        // for top location bar (like home page)
        var that = this,
            GoogleLocations = new W.Common.GoogleLocations({$input: $('#location').get(0)});

        GoogleLocations.initGoogleAutocomplete(
            function (autocomplete, $input) {
                var $el = $($input),
                    address = GoogleLocations.getAddressFromAutocomplete(autocomplete);

                $el.val(W.common.Format.formatAddress(address));
                $el.blur();

                that.updateTimezone(GoogleLocations, address, function () {
                    that.saveUserLocation(address);
                });
            },
            function (results, status, $input) {
                if (status === 'OK') {
                    var $el = $($input),
                        address = GoogleLocations.getAddressFromPlace(results[0]);

                    $el.val(W.common.Format.formatAddress(address));
                    $el.blur();

                    that.updateTimezone(GoogleLocations, address, function () {
                        that.saveUserLocation(address);
                    });
                }
            },
            function ($input) {
                var $removeBtn = $('.remove-location');
                $('.check').hide();
                $removeBtn.removeClass('hidden');
                $removeBtn.on('click', function () {
                    if (!that.authenticated) {
                        Cookies.remove('user_geo_location');
                    }

                    $removeBtn.addClass('hidden');
                    $('.check').show();
                    $($input).val('');
                });
            });
    },
    initDispLocation: function initDispLocation() {
        // for dispensary lookup location
        var that = this,
            GoogleLocations = new W.Common.GoogleLocations({$input: $('#disp-location').get(0)});

        GoogleLocations.initGoogleAutocomplete(
            function (autocomplete, $input) {
                var $el = $($input),
                    address = GoogleLocations.getAddressFromAutocomplete(autocomplete);

                $el.val(W.common.Format.formatAddress(address));
                $el.blur();

                that.updateDispLocationTime(GoogleLocations, address);
            },
            function (results, status, $input) {
                if (status === 'OK') {
                    var $el = $($input),
                        address = GoogleLocations.getAddressFromPlace(results[0]);

                    $el.val(W.common.Format.formatAddress(address));
                    $el.blur();

                    that.updateDispLocationTime(GoogleLocations, address);
                }
            },
            function ($input) {
                that.clearDispLocation();
            });
    },
    clearDispLocation: function clearDispLocation() {
        this.dispLocation = null;
        this.dispTimezone = null;
    },
    navigateToDispDetailPage: function navigateToDispDetailPage() {
        var $input = $('.lookup-input'),
            dispUrl = $input.attr('payload-url');

        if (dispUrl) {
            window.location.href = dispUrl;
        }
    },
    updateDispLocationTime: function updateDispLocationTime(GoogleLocations, address) {
        var that = this;

        this.dispLocation = {
            lat: address.lat,
            lon: address.lng
        };

        GoogleLocations.getTimezone(address.lat, address.lng, function (json) {
            that.dispTimezone = json.timeZoneId;
        });
    },
    updateTimezone: function updateTimezone(GoogleLocations, address, success) {
        var that = this;
        GoogleLocations.getTimezone(address.lat, address.lng, function (json) {
            that.timezone = json.timeZoneId;
            success();
        });
    },
    saveUserLocation: function saveUserLocation(data) {
        if (data) {
            var that = this;
            if (this.authenticated) {
                $.ajax({
                    method: 'POST',
                    url: '/api/v1/users/{0}/geo_locations'.format(that.userId),
                    data: JSON.stringify({address: data, timezone: this.timezone})
                });
            } else {
                delete data.location_raw;
                Cookies.set('user_geo_location', JSON.stringify(data));
            }
        }
    },
    getDispLocationTime: function getDispLocationTime() {
        return {
            location: this.dispLocation,
            timezone: this.dispTimezone
        };
    }
});