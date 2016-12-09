'use strict';

W.ns('W.pages');

W.pages.HomePage = Class.extend({

    init: function init(options) {
        this.location = options && options.location;
        this.authenticated = options && options.authenticated;
        this.userId = options && options.userId;

        this.initStrainLookupField();
        this.clickLookupSubmit();
        this.preFillUserLocation();
        this.changeLocation();
    },

    initStrainLookupField: function initStrainLookupField() {
        var lookupTemplate = _.template($('#strain-lookup-field').html());
        $('.strain-name-field').html(lookupTemplate({
            'lookup_placeholder': 'Example: Blue Dream, Maiu Wowie, Pineapple express'
        }));
        new W.pages.strain.StrainLookup();
    },

    clickLookupSubmit: function clickLookupSubmit() {
        var that = this;
        $('.lookup-submit').on('click', function (e) {
            e.preventDefault();
            var $input = $('.lookup-input'),
                strainName = $input.val(),
                strainSlug = $input.attr('payload-slug');

            if (strainName && strainSlug) {
                window.location.href = '/search/strain/{0}'.format(strainSlug);
            }
        });
    },

    preFillUserLocation: function preFillUserLocation() {
        var l = this.location;
        if (l) {
            $('.your-location-value').val('{0}, {1}, {2}'.format(l.street1, l.city, l.state));
        }
    },

    changeLocation: function changeLocation() {
        var that = this,
            $locationInput = $('#location').get(0),
            autocomplete = new google.maps.places.Autocomplete($locationInput);

        autocomplete.addListener('place_changed', function () {
            var place = autocomplete.getPlace(),
                street1 = '', zipcode = '', state = '', city = '';

            if (place.address_components) {
                $.each(place.address_components, function (i, address_comp) {
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
            }

            that.saveUserLocation({
                street1: street1,
                city: city,
                state: state,
                zipcode: zipcode,
                lat: place.geometry && place.geometry.location.lat(),
                lng: place.geometry && place.geometry.location.lng(),
                location_raw: JSON.stringify(place)
            });
        });
    },

    saveUserLocation: function saveUserLocation(data) {
        var that = this;
        if (this.authenticated) {
            $.ajax({
                method: 'POST',
                url: '/api/v1/users/{0}/geo_locations'.format(that.userId),
                data: JSON.stringify(data)
            });
        } else {
            delete data.location_raw;
            Cookies.set('user_geo_location', JSON.stringify(data));
        }
    }
});
