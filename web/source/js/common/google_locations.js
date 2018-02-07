'use strict';

W.ns('W.Common');

W.Common.GoogleLocations = Class.extend({

    init: function init(options) {
        if (!options || !options.$input) {
            console.error('$input is required to use location autocomplete');
        }

        this.$input = options && options.$input;
        this.autocomplete = new google.maps.places.Autocomplete(this.$input);
        this.pacContainerIndex = options && options.pacContainerIndex;
    },

    initGoogleAutocomplete: function initGoogleAutocomplete(onPlaceChange, onEnterKey, onLocationRemove) {
        var that = this;

        this.onPlaceChange = onPlaceChange;
        this.onEnterKey = onEnterKey;
        this.onLocationRemove = onLocationRemove;

        google.maps.event.addDomListener(this.$input, 'keydown', function (e) {
            if (e.keyCode === 13) {
                e.preventDefault();

                var place = that.autocomplete.getPlace();
                if (!place || !place.address_components) {
                    var firstResult, $pacs,
                        geoCoder = new google.maps.Geocoder();

                    if (that.pacContainerIndex && that.pacContainerIndex >= 0) {
                        $pacs = $('.pac-container');
                        firstResult = $($pacs[that.pacContainerIndex]).find('.pac-item:first').text()
                    } else {
                        firstResult = $('.pac-container .pac-item:first').text();
                    }

                    geoCoder.geocode({"address": firstResult}, function (results, status) {
                        if (that.onEnterKey) {
                            that.onEnterKey(results, status, that.$input);
                        }
                    });
                }
            }
        });

        this.autocomplete.addListener('place_changed', function () {
            that.onPlaceChange(that.autocomplete, that.$input);
        });

        $(this.$input).on('change paste keyup', function (e) {
            e.preventDefault();
            if ($(this).val() && that.onLocationRemove) {
                that.onLocationRemove(that.$input);
            }
        });
    },

    getAddressFromAutocomplete: function getAddressFromAutocomplete() {
        var that = this, place = this.autocomplete.getPlace();

        if (place && place.address_components) {
            return this.getAddressFromPlace(place);
        } else {
            var firstResult, $pacs,
                geoCoder = new google.maps.Geocoder();

            if (this.pacContainerIndex && this.pacContainerIndex >= 0) {
                $pacs = $('.pac-container');
                firstResult = $($pacs[this.pacContainerIndex]).find('.pac-item:first').text()
            } else {
                firstResult = $('.pac-container .pac-item:first').text();
            }

            geoCoder.geocode({"address": firstResult}, function (results, status) {
                if (status !== 'OK') {
                    alert('Invalid address');
                } else {
                    if (this.onEnterKey) {
                        this.onEnterKey(results, status, that.$input);
                    }
                }
            });
        }
    },

    getAddressFromPlace: function getAddressFromPlace(raw_place) {
        var street1 = '', zipcode = '', state = '', city = '', aal3 = '';
        $.each(raw_place.address_components, function (i, address_comp) {
            if (_.includes(address_comp.types, 'street_number')) {
                street1 += address_comp.long_name + ' ';
            }

            if (_.includes(address_comp.types, 'route')) {
                street1 += address_comp.long_name;
            }

            if (_.includes(address_comp.types, 'postal_code') && zipcode === '') {
                zipcode = address_comp.long_name;
            }

            if (_.includes(address_comp.types, 'administrative_area_level_1') && state === '') {
                state = address_comp.short_name;
            }

            if (_.includes(address_comp.types, 'locality') && city === '') {
                city = address_comp.long_name;
            }

            if (_.includes(address_comp.types, 'administrative_area_level_3') && aal3 === '') {
                aal3 = address_comp.long_name;
            }
        });

        debugger;
        return {
            street1: street1,
            city: city || aal3,
            state: state,
            zipcode: zipcode,
            lat: raw_place.geometry && raw_place.geometry.location.lat(),
            lng: raw_place.geometry && raw_place.geometry.location.lng(),
            location_raw: JSON.stringify(raw_place)
        };
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
