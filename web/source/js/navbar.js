'use strict';

W.ns('W');

W.Navbar = function () {

    return {
        init: function init(options) {
            var that = this;
            options = options || {};

            that.authenticated = options.authenticated;
            that.location = options.location;
            that.userId = options.userId;

            if (that.authenticated && options.locationUpdate) {
                that.getLocation(
                    function(location) {
                        that.location = location;
                        that.updateAddress(location.address);
                        that.clickUpdateLocation();
                        $('.update-location-href').removeClass('hidden');
                    },
                    function() {
                        $('.action.location').addClass('hidden');
                    }
                );
            }

            this.hamburgerMenuClickHandler();
        },

        updateAddress: function (location) {
            var location_parts = [];
            if (!location) {
                return;
            }

            $('.nav-bar-user-street').text(location.street1 || '');

            location_parts.push(location.city || '');
            location_parts.push(location.state || '');
            location_parts.push(location.zipcode || '');

            if (location_parts.length === 0 && location.location_raw && !_.isEmpty(location.location_raw)) {
                var parsed = JSON.parse(location.location_raw);
                if (parsed && parsed[0] && parsed[0].formatted_address) {
                    location_parts.push(parsed[0].formatted_address);
                }
            }

            $('.nav-bar-user-location').text(location_parts.join(', '));
        },

        hamburgerMenuClickHandler: function hamburgerMenuClickHandler() {
            var menuSelector = $('.nav-list-wrapper .mobile-menu');

            $(document).click('click tap', function (e) {
                if ($(window).width() > 480) {
                    return;
                }

                var $target = $(e.target);
                var navList = $('.nav-list');

                if ($target.is(menuSelector) || $target.closest(menuSelector).length) {
                    if (navList.css('display') === 'block') {
                        navList.css('display', 'none');
                    } else {
                        navList.css('display', 'block');
                    }
                } else {
                    navList.css('display', 'none');
                }
            })

        },

        getLocation: function getLocationAddress(success, failure) {
            var that = this;

            navigator.geolocation.getCurrentPosition(function (position) {
                var geoCoder = new google.maps.Geocoder(),
                    pos = {lat: position.coords.latitude, lng: position.coords.longitude};

                geoCoder.geocode({'location': pos}, function (results, status) {
                    if (status === 'OK') {
                        if (results) {
                            var address = that.buildAddress(results);
                            that.getTimezone(position.coords.latitude, position.coords.longitude, function (json) {
                                success({
                                    address: {
                                        lat: position.coords.latitude,
                                        lng: position.coords.longitude,
                                        location_raw: JSON.stringify(results),
                                        street1: address.street1,
                                        city: address.city,
                                        state: address.state,
                                        zipcode: address.zipcode
                                    },
                                    timezone: json.timeZoneId || ''
                                });
                            });
                        }
                    } else {
                        failure();
                    }
                });
            }, failure);
        },

        clickUpdateLocation: function clickUpdateLocation() {
            var that = this;
            $('.update-location-href').on('click', function (e) {
                that.saveUserLocation(that.location);
            });
        },

        buildAddress: function buildAddress(results) {
            var zipcode = '', city = '', state = '', street1 = '', aal3 = '';
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

                if (_.includes(res.types, 'administrative_area_level_3') && city === '') {
                    $.each(res.address_components, function (j, address_comp) {
                        if (_.includes(address_comp.types, 'administrative_area_level_3')) {
                            aal3 = address_comp.long_name;
                        }
                    });
                }
            });

            return {city: city || aal3, state: state, zipcode: zipcode, street1: street1};
        },

        saveUserLocation: function saveUserLocation(location) {
            var that = this,
                locationRaw = location.address.location_raw,
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
                    data: JSON.stringify(location)
                });
            } else {
                Cookies.set('user_geo_location', JSON.stringify(location.address));
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
    };
}();
