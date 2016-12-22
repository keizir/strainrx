'use strict';

W.ns('W.Common');

W.Common.GoogleLocations = function () {

    return {
        initGoogleAutocomplete: function initGoogleAutocomplete($input, onLocationChange) {
            var autocomplete = new google.maps.places.Autocomplete($input);

            google.maps.event.addDomListener($input, 'keydown', function (e) {
                if (e.keyCode == 13) {
                    e.preventDefault();
                    onLocationChange(autocomplete);
                }
            });

            autocomplete.addListener('place_changed', function () {
                onLocationChange(autocomplete);
            });
        },

        getAddressFromAutocomplete: function getAddressFromAutocomplete(googleAutocomplete) {
            var place = googleAutocomplete.getPlace();

            if (place && place.address_components) {
                return this.getAddressFromPlace(place);
            } else {
                alert('Invalid Location');
            }
        },

        getAddressFromPlace: function getAddressFromPlace(raw_place) {
            var street1 = '', zipcode = '', state = '', city = '';
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
            });

            return {
                street1: street1,
                city: city,
                state: state,
                zipcode: zipcode,
                lat: raw_place.geometry && raw_place.geometry.location.lat(),
                lng: raw_place.geometry && raw_place.geometry.location.lng(),
                location_raw: JSON.stringify(raw_place)
            };
        }
    };
}();
