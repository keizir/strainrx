'use strict';

W.ns('W');

W.Navbar = function () {

    return {
        init: function init(options) {
            this.authenticated = options && options.authenticated;
            this.location = options && options.location;
            this.userId = options && options.userId;

            if (AUTHENTICATED && !EMAIL_VERIFIED) {
                $('.strain-wizard-link').on('click', function (e) {
                    e.preventDefault();
                    W.common.VerifyEmailDialog();
                });
            }

            this.hamburgerMenuClickHandler();
        },

        updateAddress: function (location) {
            var l = location || this.location, location_parts = [];
            if (l) {
                if (l.street1) {
                    $('.nav-bar-user-street').text(l.street1);
                }

                if (l.city) {
                    location_parts.push(l.city);
                }

                if (l.state) {
                    location_parts.push(l.state);
                }

                if (l.zipcode) {
                    location_parts.push(l.zipcode);
                }

                if (location_parts.length === 0 && l.location_raw && !_.isEmpty(l.location_raw)) {
                    var parsed = JSON.parse(l.location_raw);
                    if (parsed && parsed[0] && parsed[0].formatted_address) {
                        location_parts.push(parsed[0].formatted_address);
                    }
                }

                $('.nav-bar-user-location').text(location_parts.join(', '));
            }
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

        clickUpdateLocation: function clickUpdateLocation() {
            var that = this;
            $('.update-location-href').on('click', function (e) {
                e.preventDefault();
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

                                    that.updateAddress(address);
                                });
                            }
                        } else {
                            console.log('Geocoder failed due to: ' + status);
                        }
                    });
                }, function () {
                    console.log('Cannot locate user');
                });
            });
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
    };
}();
