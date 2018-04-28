'use strict';

W.ns('W.views');

W.views.LocationView = W.views.BaseLocationView.extend({

    init: function (options) {
        this.authenticated = options && options.authenticated;
        this.userId = options && options.userId;
        this.location = options && options.location;

        if (!this.location) {
            this.getUserLocation();
        }

        this.preFillUserLocation();
        this.onChangeLocation();
    },

    updateTimezone: function updateTimezone(GoogleLocations, address, success) {
        var that = this;
        if (typeof address !== 'undefined' && address.lat && address.lng) {
            GoogleLocations.getTimezone(address.lat, address.lng, function (json) {
                that.timezone = json.timeZoneId;
                success();
            });
        }
    },

    onChangeLocation: function onChangeLocation() {
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

    preFillUserLocation: function preFillUserLocation() {
        if (this.location) {
            $('.your-location-value').val(W.common.Format.formatAddress(this.location)).trigger('change');
        }
    },

    getUserLocation: function getUserLocation() {
        var that = this;

        that.getLocation(function (data) {
            that.timezone = data.timezone;
            that.saveUserLocation(data.address);
        }, function () {
            console.log('Cannot locate user');
        });
    },

    saveUserLocation: function saveUserLocation(data) {
        var that = this,
            locationRaw = data.location_raw,
            $locationInput = $('.your-location-value');

        if (locationRaw) {
            var parsed = JSON.parse(locationRaw);
            if (parsed && parsed[0] && $locationInput) {
                $locationInput.val(parsed[0].formatted_address).trigger('change');
            }
        }

        if (this.authenticated) {
            $.ajax({
                method: 'POST',
                url: '/api/v1/users/{0}/geo_locations'.format(that.userId),
                data: JSON.stringify({address: data, timezone: that.timezone || ''})
            });
        } else {
            delete data.location_raw;
            Cookies.set('user_geo_location', JSON.stringify(data));
        }
    }
});