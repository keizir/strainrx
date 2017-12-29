'use strict';

W.ns('W.views');

W.views.LocationView = Class.extend({

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
        GoogleLocations.getTimezone(address.lat, address.lng, function (json) {
            that.timezone = json.timeZoneId;
            success();
        });
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

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                var geoCoder = new google.maps.Geocoder(),
                    pos = {lat: position.coords.latitude, lng: position.coords.longitude};

                geoCoder.geocode({'location': pos}, function (results, status) {
                    if (status === 'OK') {
                        if (results) {
                            var address = that.buildAddress(results);
                            that.getTimezone(position.coords.latitude, position.coords.longitude, function (json) {
                                that.timezone = json.timeZoneId;

                                that.saveUserLocation({
                                    lat: position.coords.latitude,
                                    lng: position.coords.longitude,
                                    location_raw: JSON.stringify(results),
                                    street1: address.street1,
                                    city: address.city,
                                    state: address.state,
                                    zipcode: address.zipcode
                                });
                            });
                        }
                    } else {
                        console.log('Geocoder failed due to: ' + status);
                    }
                });
            }, function () {
                console.log('Cannot locate user');
            });
        } else {
            console.log('Browser doesn\'t support Geolocation');
        }
    },

    buildAddress: function buildAddress(results) {
        var zipcode = '', city = '', state = '', street1 = '';
        $.each(results, function (i, res) {
            if (_.includes(res.types, 'postal_code') && zipcode === '') {
                $.each(res.address_components, function (j, address_comp) {
                    if (_.includes(address_comp.types, 'postal_code')) {
                        zipcode = address_comp.long_name;
                    }
                });
            }

            if (_.includes(res.types, 'administrative_area_level_1') && state === '') {
                $.each(res.address_components, function (j, address_comp) {
                    if (_.includes(address_comp.types, 'administrative_area_level_1')) {
                        state = address_comp.short_name;
                    }
                });
            }

            if (_.includes(res.types, 'locality') && city === '') {
                $.each(res.address_components, function (j, address_comp) {
                    if (_.includes(address_comp.types, 'locality')) {
                        city = address_comp.long_name;
                    }
                });
            }

            if (_.includes(res.types, 'street_address') && city === '') {
                $.each(res.address_components, function (j, address_comp) {
                    if (_.includes(address_comp.types, 'street_number')) {
                        street1 += address_comp.long_name + ' ';
                    }

                    if (_.includes(address_comp.types, 'route')) {
                        street1 += address_comp.long_name;
                    }
                });
            }
        });

        return {city: city, state: state, zipcode: zipcode, street1: street1};
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
    },

    getTimezone: function getTimezone(lat, lng, callback) {
        var xsr = new XMLHttpRequest();
        xsr.open(
            'GET',
            'https://maps.googleapis.com/maps/api/timezone/json?location={0},{1}&timestamp={2}&key={3}'
                .format(lat, lng, '1458000000', GOOGLE_API_KEY));

        xsr.onload = function () {
            callback(JSON.parse(xsr.responseText));
        };

        xsr.send();
    }
});